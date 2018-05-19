import re
import sqlite3
import numpy as np
import pandas as pd

#########################################################
#       FUNCTIONS DEALING MEAL_INFO (FORMERLY MEAL_DF)
#########################################################
def my_print_function(s):
    print(s)

'''
simplify_duration
    Sets Duration value to its average instead of a range.
'''
def simplify_duration(d):
    d = d.split('-')
    if len(d)>1:
        return int(int(d[1])+int(d[0])/2)
    else:
        return int(d[0][:-1])

#########################################################
#       FUNCTIONS DEALING WITH THE DATABASE
#########################################################
'''
get_sql_table_columns(db_name,table_name):
    GET COLUMNS OF table_name

save_3_tables(dbname, meal_info, meal_ing, ingredients):
    Saves the 3 tables in the dbname.sqlite.

load_3_dataframes :
    Receives the name of the sqlitefile
    Returns the specific 3 tables: meal_info, meal_ing and ingredients
    as dataframes.

show_db_tables
    Receives as parameter the name of the sqlite file
    Prints out the tables the database has.

build_create_query
    Receives as parameters:
        table_name: Name of the table to be created in sqlite database
        dataframe:  The dataframe destined to be in the table.
        flag_id:    If true, primary key is set to the index
    Returns a the fashioned query capable to create the requested table
'''

def get_sql_table_columns(db_name,table_name):
    get_col_query = 'select * from {t1}'.format(t1=table_name)
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    c = conn.execute(get_col_query)
    row = c.fetchone()
    return row.keys()

def save_3_tables(db_name, meal_info, meal_ing, ingredients):
    conn = sqlite3.connect(db_name)
    meal_info.to_sql("meal_info", conn, if_exists="replace")
    meal_ing.to_sql("meal_ing", conn, if_exists="replace")
    ingredients.to_sql("ingredients", conn, if_exists="replace")
    conn.commit()
    conn.close()
    print('Tables Saved to',db_name)

def show_db_tables(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    query_check  = 'SELECT name FROM sqlite_master WHERE type= "table";'
    c.execute(query_check)
    table_set = [item[0] for item in c.fetchall()]
    print(table_set)

def build_create_query(table_name, df, flag_id):
    my_query = 'CREATE TABLE'+' '+table_name+' '+'('
    for ind, col in enumerate(df.columns):
        col_ = re.sub(' ','_',col)
        # Get a real sample of the column value to determine its data type
        my_s = df[col][~df[col].isnull()]
        val_ = my_s.values[0]
        if isinstance(val_, str):
            type_name = ' TEXT'
        elif isinstance(val_, np.int64):
            type_name = ' INTEGER'
        else:
            type_name = ' REAL'
        if flag_id == True and ind == 0:
            pk = ' PRIMARY KEY,'
        else:
            pk = ','
        my_query += ' ' + col_.lower() + type_name + pk
    return my_query.rstrip(',')+')'

def load_3_dataframes(db_name = 'project2.sqlite'):
    table_name_1  = 'meal_info'
    table_name_2  = 'meal_ing'
    table_name_3  = 'ingredients'
    id_field      = 'meal_id'
    show_db_tables(db_name)
    q1 = 'SELECT * FROM {tn} ORDER BY {idf}'.format(tn=table_name_1, idf=id_field)
    q2 = 'SELECT * FROM {tn} ORDER BY {idf}'.format(tn=table_name_2, idf=id_field)
    q3 = 'SELECT * FROM {tn}'.format(tn=table_name_3)
    conn = sqlite3.connect(db_name)
    # Load Meal_info Dataframe
    meal_info = pd.read_sql_query(q1, conn)
    meal_info = meal_info.drop('index', axis=1)
    # Load Meal_ing Dataframe
    meal_ing = pd.read_sql_query(q2, conn)
    meal_ing = meal_ing.drop('index', axis=1)
    # Load Ingredients Dataframe
    ingredients = pd.read_sql_query(q3, conn)
    ingredients = ingredients.drop('index', axis=1)
    conn.close()
    return meal_info, meal_ing, ingredients

#########################################################
#        FUNCTIONS TO PROCESS THE INGREDIENTS
#########################################################
'''
identify_ingredients
    Receives the ingredients as a whole sentence and divides it in said smaller segments.

get_part_of_ingredient
    This function splits the string s1 by tabs
    (i.e. qty\tmsr\ttyp\ting\tshp) and returns the item on the indx place.

fusion_plural_to_singular_ingredients
    Receives as parameter the dataframe meal_ing
    Modifies every main ingredient if it has a singular and plural form by changing
    the plural form to its singular homologue.

convert_char_fraction_to_float
    Receives as parameter

build_ingredients_dataframe(meal_ing)
    Gets as parameter the meal_ingredients dataframe and
    selects the unique main ingredients
    to store it in a new dataframe along with a unique Id of 4 characters,
        1st: first letter of the ingredient
        2nd: length of the ingredient (if length is 12 it will be reduced to 1+2=3)
        3rd: ord(last letter)
        4th: number of row
'''

def identify_ingredients(ing):
# The next variables will define the pattern to search in the ingredients segment
# for identification
    quantity_pattern = r'\bfrac\d+|\d\.\d+|\d+|'+'|'.join(fraction_list)
    unit_pattern     = r"'\bear\b'|"+'|'.join(measure_units)
    shape_pattern    = r""+'|'.join(shape_ing)
    type_pattern     = r""+'|'.join(type_ing)
    qty = msr = shp = typ = ''
    # Get the QTY
    r = re.search(r"&|;", ing)
    if r:
        # Correct the bug of 1&frac45 numbers
        f = ing.split()[0]
        if r.start() == 0:
            qty = round(int(f[-3])/int(f[-2]), 1)
        else:
            qty = round(int(f[0])+(int(f[-3])/int(f[-2])),1)
        ing = ing[len(f):].lstrip(' ')
    else:
        r = re.search(quantity_pattern, ing)
        qty = ing[r.start():r.end()]
        ing = ing[r.end()+1:]
    # Get rid of anything within parenthesis
    r = re.search(r"\(.{1,10}\)", ing)
    if r:
        ing = ing[:r.start()-1]
    # GET Unit of Measure
    r = re.findall(unit_pattern,ing)
    if r:
        msr = ' '.join(r)
        temp_ing = ing.split(msr)
        ing = ''.join(temp_ing).lstrip(' ').rstrip(' ')
    # Get the texture or shape
    if len(ing.split()) > 1:
        r = re.findall(shape_pattern, ing)
        if r:
            shp = ' '.join(r)
            temp_ing = ing.split(shp)
            ing = ''.join(temp_ing).lstrip(' ').rstrip(' ')
    # Assign the remainings to type and main_ingredient variables.
    if len(ing.split()) > 1:
        typ = ' '.join(ing.split()[:-1])
        temp_ing = ing.split()[-1]
        ing = ''.join(temp_ing).lstrip(' ').rstrip(' ')
    return str(qty)+'\t'+msr+'\t'+typ+'\t'+ing+'\t'+shp

def get_part_of_ingredient(indx, s1):
    s = s1.split('\t')
    if s[indx] != '':
        return s[indx]
    else:
        return np.nan

def fusion_plural_to_singular_ingredients(meal_ing):
    s = meal_ing.loc[:,['Meal_id','Ming']].sort_values('Ming').reset_index()
    for ind in range(len(s)-1):
        if s.loc[ind,'Ming']+'s'==s.loc[ind+1,'Ming'] or s.loc[ind,'Ming']+'es'==s.loc[ind+1,'Ming']:
            a = s.loc[ind,'Ming']
            b = s.loc[ind+1,'Ming']
        meal_ing.loc[(meal_ing.Ming == a) | (meal_ing.Ming == b),'Ming'] = a
    return meal_ing

def convert_char_fraction_to_float(frac_str):
    try:
        return float(frac_str)
    except:
        return unicodedata.numeric(frac_str)

def build_ingredients_dataframe(meal_ing):
    # Getting a list of unique ingredients.
    i2 = meal_ing.Ming.sort_values().unique()
    # Cleaning data, getting rid of everything that is not text.
    i3 = re.findall(r"\w+-\w+|\w+", ' '.join(i2))
    # Converting it back to a Series
    ingredients = pd.DataFrame(i3, columns = ['Ming'])
    # Adding a unique ID
    ingredients['ing_id']=[row[:2]+str(len(row))+str(row[-1])+str(ind) for ind, row in enumerate(ingredients['Ming'])]
    return ingredients







#########################################################
#                   WEB SCRAPING FUNCTIONS
#########################################################
def get_meal_overview(meal_ov, idx, w0, w1):
#    print('get_meal_overview')
    while idx < len(meal_ov):
        mov = meal_ov[idx].get_text().lower().split()
        if mov != [] and (mov[0] == w0 and mov[1] == w1):
            return meal_ov[idx+1].get_text().lower().split()[0], idx+1
        idx += 1
    return 0

def get_single_meal_id(meal):
    m_id = meal.select('a.button.link--inverse.list--share__link')
    s = m_id[0].get('href')
    r = re.search(r"/\d+/",s)
    if r:
        return s[r.start():r.end()].rstrip('/').lstrip('/')
    else:
        print('Meal_id not found')
        return np.nan

def get_meal_overview_and_ingredients(meal, mId):

    # Meal Overview
    meal_ov = meal.select('div.meal__overviewItem span')
    if meal_ov == []: # Some cases where the recipe is so logic that doesnt need info (i.e spring fruit basket)
        return [0,0]
    ## 2 is time, 4 is within days, 6 or 7 is level, 13 or 14 is spicy 18 ends
    time_spent, idx = get_meal_overview(meal_ov, 0, 'cook', 'time:')
    expire,     idx = get_meal_overview(meal_ov, idx, 'cook','within:')
    exp_level,  idx = get_meal_overview(meal_ov, idx,'difficulty', 'level:')
    spicy,      idx = get_meal_overview(meal_ov, idx,'spice', 'level:')

    # Meal Ingredients
    meal_ing = meal.select('ul.list--unstyled.group.position--relative.text--center--bpDown2 li')
    ing_list = []
    for ingredient in meal_ing:
        ### example of ingredient: ['info', '3¾', 'oz.', "font'ina", 'cheese', 'slices']
        ing = ingredient.get_text().lower().replace("info","").replace("'","_").split()
        ing_list.append(' '.join(ing))
    return ing_list, [time_spent, expire, exp_level, spicy]
