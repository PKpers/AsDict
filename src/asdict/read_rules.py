from .exceptions import BlockError, StructureError
### Create functions, so that the dict is read following the dict file rules ###
def as_type(var, dtype):
    dtypes = ['str', 'float', 'bin', 'int']
    if dtype not in dtypes:
        raise TypeError("Unsupported data type '{}' in {}".format(dtype, filename))
        exit()
    #
    if dtype=='str':
        var = str(var)
    elif dtype=='float':
        var = float(var)
    elif dtype=='bin':
        try:
            var = bin(var)
        except Exception:
            var = bin(int(var))
        except Exception:
            raise TypeError("Cannot convert '{}' to binary.".format(var))
        #
        #
    elif dtype=='int':
        var = int(var)
    #
    return var
#
def evaluate_key(key, dtype, filename):
    if 'int' in dtype or 'str' in dtype:
        exception = 'Key data type is not compatible with the one specified in head'
        key = try_as_type(key, dtype, exception)
    elif dtype == "Mixed":
        try:
            key = as_type(key, 'int')
        except Exception:
            key = as_type(key, 'str')
        except Exception:
            raise TypeError("Unsuported data type '{}' for dict keys".format(dtype))
        #
    else:
        raise TypeError("Unsuported data type '{}' for dict keys".format(dtype))
    return key
#
def try_as_type(key, dtype, exception):
    try:
        result = as_type(key, dtype)
        return result
    except Exception:
        raise Exception(exception)

def get_keys(dict_file, dtype, filename):
    if dtype == 'mixed':
        raise NameError('In {}, Perhaps you ment "{}"?'.format(filename, 'Mixed'))
    #
    keys = []
    key_count = 0
    before_k = None
    #
    for i, k in enumerate(dict_file):
        if i !=0: prev_line = dict_file[i-1]
        # does it have a key
        if '[' in k and ']' in k :
            key_count += 1
            #
            # is the synrax correct
            # A propper key shoud be enclosed by brackets
            if  ']\n' not in k:
                raise SyntaxError('invalid syntax in {}: {}'.format(filename, k)) 
            #
            # If the key block doesn't start with [ then its wrong
            if k[0] != '[':
                raise SyntaxError('invalid syntax in {}: {}'.format(filename, k)) 
            #
            # Before the first key there should be either a blank line or a head block
            if key_count ==1 and prev_line != '\n' and '* With' not in prev_line:
                raise StructureError('Invalid structure In {}: {} '.format(filename, prev_line))
            #
            # Before the keys(except the first one) there shuld be a #.
            if key_count > 1 and prev_line != '#\n' :
                raise StructureError('Invalid structure In {}: {}'.format(filename, prev_line))
            #
            # Does it make sense?
            # Evaluate the key block
            key =k.split('[')[1].split(']')[0]
            key_eval = evaluate_key(key, dtype, filename)
            keys.append(key_eval)
        #
    #
      
    if key_count == 0:
        raise StractureError('Invalid stracture, in {}. No keys found'.format(filename))
    #
    return keys
#

def is_item(i, it_char, filename):
    special_chars = '!@#$%^&*(){}[]|\|/?.,<>:;-+="' + "'"
    numbers = '1234567890'
    poss_name, poss_obj = i.split(it_char)
    #
    # items name, <name>, shuld not start with special chars or numbers
    if poss_name[0] in special_chars or poss_name[0] in numbers:
        raise SyntaxError('Invalid syntax in {}: {}'.format(filename, i))
    #
    # no spaces between name, =, !, and dtype
    if poss_name[-1] == ' ' or poss_obj[0] == ' ':
        raise SyntaxError('Invalid syntax in {}: "{}"'.format(filename, i))
    #
    # items content shuld be enclosed in "".
    if poss_obj[-2] != '"': #poss_obj[-1] == '\n'
        raise SyntaxError('Invalid syntax in {}: "{}"'.format(filename, i))
    #
    if ' "' not in poss_obj:
        if it_char == '=':
            return poss_obj
        raise SyntaxError('Invalid syntax in {}: "{}"'.format(filename, i))
    #
    return poss_obj

def check_structure(item_count, prev_line, raw_items, filename):
    # Key block must be followed by items. 
    if item_count == 1 and '[' and ']\n' not in prev_line :
        raise StructureError('Invalid structure in {}: "{}"'.format(filename, prev_line))
    #
    # Item must be followed by item or '#'
    if item_count >1 and prev_line not in raw_items:
        raise StructureError(
            'Invalid structure in {}: "{}". Items should be followed by items or end element symbol "#"'\
            .format(filename, i))
    #
    return

def get_items_headless(dict_file, filename):
    quotation = '"'
    items_part=[]
    items = []
    raw_items = []
    item_count = 0
    prev_line = None
        #
    for n, i in enumerate(dict_file):
        if n != 0: prev_line = dict_file[n-1]
        if '= !' in i:
            raise SyntaxError('Invalid syntax in {}'.format(filename))
        #
        if '=!' in i:
            # Ensure that i is item and check syntax
            obj=is_item(i, '=!', filename)
            raw_items.append(i)
            item_count += 1
            #
            check_structure(item_count, prev_line, raw_items, filename)
            # Evaluate <item>
            try:
                dtype, item = obj.split(' ')
            except Exception:
                raise SyntaxError('Invalid syntax in {}.'.format(filename))
            #
            item = as_type(item.split(quotation)[1], dtype)
            items_part.append(item)
        #
        # Is is end element operator
        if '#' in i:
            #Check syntax
            if prev_line not in raw_items:
                raise StructureError('Invalid Structure in {}: "{}". "#" shouldnt be here'.format(filename, i))
            #
            # Evaluate
            if len(items_part) == 1:
                items_part = items_part[0]
                items.append(items_part)
            else:
                items_part = tuple(items_part)
                items.append(items_part)
            #
            items_part = []
            item_count = 0
        #
    #
    return items
#
def get_items_w_head(dict_file, dtype, filename):
    quotation = '"'
    items = []
    items_part = []
    raw_items = []
    item_count = 0
    prev_line = None
    for n, i in enumerate(dict_file):
        if n != 0: prev_line = dict_file[n-1]
        if '=' in i:
            # Ensure that i is item and check syntax
            obj = is_item(i, '=', filename)
            raw_items.append(i)
            item_count += 1
            #
            check_structure(item_count, prev_line, raw_items, filename)
            #
            try: 
                item = obj.split(quotation)[1]
            except Exception:
                raise SyntaxError('Invalid syntax in {}.'.format(filename))
            #
            item = as_type(item, dtype)
            items_part.append(item)
        #
        if '#' in i:
            #Check syntax
            if prev_line not in raw_items:
                raise StructureError('Invalid structure in {}: "{}". "#" shouldnt be here'.format(filename, i))
            #
            # Evaluate
            if len(items_part) == 1:
                items_part = items_part[0]
                items.append(items_part)
            else:
                items_part = tuple(items_part)
                items.append(items_part)
                #
            items_part = []
            item_count = 0
        #
    #
    return items
#
def get_items(dict_file, head_info, filename):
    items = ''
    if 'no default' in head_info:
        items = get_items_headless(dict_file, filename)
    else:
        items =get_items_w_head(dict_file, head_info, filename)
    #
    return items
#
def get_head(dict_file, filename):
    #Does the file have a head?
    head = [h for h in dict_file if '* With' in h]
    if len(head) == 0:
        raise StructureError('Can not find Head block in {}.'.format(filename))
    # 
    key_default = 'no default'
    item_default = 'no default'
    #
    # Acceptable head syntax  
    key_dtypes = ('str', 'int', 'Mixed')
    key_obj = ['!'+kd+ ' keys' for kd in key_dtypes]
    item_dtypes = ('str', 'int', 'float', 'bin')
    item_obj = ['!'+idt+' items' for idt in item_dtypes]

    count_keys = 0
    count_items = 0
    
    for h in head:
        # Check if given syntax maches the correct one
        # ko = !dtype obj. h = !+With+<obj>
        # Make sure that <obj> = !dtype obj and that
        # !dtype is acceptable 
        key_head = [ko in h for ko in key_obj]
        item_head = [ih in h for ih in  item_obj]
        if any(key_head)==False and any(item_head)==False:
            raise SyntaxError("Invalid syntax in {}: {}".format(filename, h))
        #
        # evaluate the head
        # This means, extract the datatypes for keys and items
        # Make sure excatly one head block for keys
        # and at most one head blcok for items
        dtype = h.split('!')[1].split(' ')[0]
        if "keys" in h or "Keys" in h:
            count_keys += 1
            key_default = dtype
        if 'items' in h or 'Items' in h:
            count_items += 1
            item_default = dtype
        #
        if count_keys != 1:
            raise BlockError('Invalid Head block in {}. \
            Exactly one head block defining the key data type should be provided'.format(filename))
        #
        if count_items >= 2:
            raise BlockError('Invalid Head block in {}. \
            At most, one head block defining item data type\
            should be provided'.format(filename))
        #
    return (key_default, item_default)

