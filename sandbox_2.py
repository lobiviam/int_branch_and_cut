list1 = ['a','b','c','d','e']
list2 = [1,2,3,4,5]
list3 = ['c', 'd']
zip_result = zip(list1, list2)
resultes = [zr_it for zr_it in zip_result if zr_it[0] not in list3]

print(resultes,"\n------------------\n", zip_result, '\n---------------------\n', zip_result[::[,1]])