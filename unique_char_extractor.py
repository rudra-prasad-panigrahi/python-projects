def unique_char_extractor(input_string):
    special_chars = "@#$%^&*()_+-+={}[]/<>?,.;:'\\/~`"
    unique_chars = ""
    for char in input_string:
        if char not in unique_chars and char not in special_chars:
            unique_chars += char
    return unique_chars 
input_string = input("Enter a string: ")
result = unique_char_extractor(input_string)
print("Unique characters in the string:", result)