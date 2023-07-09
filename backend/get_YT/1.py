input_list = [2, 3, 8, 9, 7, 6, 1, 4, 5]


odd_list = []
for num in input_list:
    if num % 2 == 0:
        continue
    else:
        odd_list.append(num)

# Sort even numbers in increasing order
odd_list.sort()
print(odd_list)


# Create the output list
output_list = []
odd_index = 0

for num in input_list:
    if num % 2 == 0:
        output_list.append(num)
    else:
        output_list.append(odd_list[odd_index])
        odd_index += 1

print(output_list)
