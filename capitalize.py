def capitalize_city_name(city_name: str):
    """
    This function correctly capitalizes names of Russian cities;
    input:
    city_name : str     name of the Russian city;
    output:
    city_name_cap : str     correctly capitalized city name
    """
    char_set = set([' ', '-'])
    def simple_capitalize(city_name_part: str):
        if city_name_part == 'на':
            return city_name_part
        return city_name_part[0].upper() + city_name_part[1:]
        
    for char in char_set:
        city_name = char.join(list(map(simple_capitalize, city_name.split(char))))
    
    city_name_cap = simple_capitalize(city_name)
    return city_name_cap
