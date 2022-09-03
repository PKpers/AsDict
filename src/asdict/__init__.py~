from read_rules import get_head, get_keys, get_items
#
def read_as_dict(filename):
    with open(filename, 'r') as f:
        lines=f.readlines()
    #
    dtype_keys, dtype_items= get_head(lines, filename)
    keys = get_keys(lines, dtype_keys, filename)
    items= get_items(lines, dtype_items, filename)
    #
    d = {}
    for i in range(len(keys)):
        d[keys[i]] = items[i]
    #
    return d 

if __name__ == "__main__":
    filename = 'example2.dict'
    test = read_as_dict(filename)
    print(test)
