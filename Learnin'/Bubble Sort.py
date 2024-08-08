def bubble_sort(list_of_nums):
    target=len(list_of_nums)-1
    check=0
    while target!=check:
        check=0
        for index in range(len(list_of_nums)-1):
            if list_of_nums[index]<=list_of_nums[index+1]:
                check+=1
            else:
                reverse=list_of_nums[index:index+2][::-1]
                list_of_nums[index]=reverse[0]
                list_of_nums[index+1] = reverse[1]
    print(list_of_nums)
