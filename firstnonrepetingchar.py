#first non repeating character
def first_non_repeating_character(input_string):
    char_count={}
    for char in input_string:
        if char in char_count:
            char_count[char]+=1
        else:
            char_count[char]+=1
    for char in input_string:
        if char_count[char]==1:
            return char
    return "All characters are repeating"
input_string=input("Enter a string: ")
print("First non-repeating character:",first_non_repeating_character(input_string))

