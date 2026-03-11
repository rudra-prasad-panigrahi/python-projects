#string pattern validator
def string_pattern_validator(string,pattern):
    if pattern is string:
        return "pattern is found in the string"
    else:
        return "pattern is not found in the string"
pattern=input("enter the pattern to search: ")
string=input("enter the string: ")
print(string_pattern_validator(string,pattern))