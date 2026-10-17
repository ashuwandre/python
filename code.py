# # %%
# import random

 

# import random
# y_test = [random.randint(0,1) for _ in range(100)]
# y_actual = [random.randint(0,1) for _ in range(100)]

# # %%
# fp=fn=tp=tn=0
# for i in range(0,len(y_test)):
#     if (y_test[i]==1) and (y_actual[i])==0:
#         fp +=1
#     if (y_test[i])==0 and (y_actual[i])==1:
#         fn += +1
#     if (y_test[i])==1 and (y_actual[i])==1:
#         tp += +1
#     if (y_test[i])==0 and (y_actual[i])==0:
#         tn += +1
        
# accuracy = (tp+tn)/(len(y_test))
# precision = (tp)/(tp+fp)
 
# recall = tp / (tp + fn)

# f1 = 2 * precision * recall / (precision + recall)
# print(accuracy)
# print(precision)
# print(recall)
# print(f1)
 
 
 
 

# # %%
# from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score

# # Actual labels
# y_true = y_actual

# # Predicted labels
# y_pred = y_test

# print("Accuracy :", accuracy_score(y_true, y_pred))
# print("Precision:", precision_score(y_true, y_pred))
# print("Recall   :", recall_score(y_true, y_pred))
# print("F1 Score :", f1_score(y_true, y_pred))

# # %%
# names = [
#     " Bob ",
#     "bob",
#     "Alice",
#     " alice ",
#     "CHARLIE",
#     "Charlie",
#     "BOB",
#     "Charlie "
# ]
# names

# # %%
# import copy
# dedup = []

# other = []

# for i in names:
#     k = i.strip().lower()
#     if k not in other:
#         print('true')
#         print(dedup)
      
         
#         dedup.append(i)
#         other.append(k)
#     print()
# print(dedup)
 

# # %%
# name = 'python'
# res = ''
# for i in name:
#     res = i+res 
# print(res)

# # %%
# name = 'python And data science'
# res = ''
# for i in name:
#     if i  in ['a','e','i','o','u','A','E','I','O','U']:
        
#         res = res + i
# print(res)

# # %%
# [i for i in range(1,50) if all(i% n**int(len(l)+1)]

# # %%
# arr1 = [1, 2, 3, 4, 5, 6]
# arr2 = [4, 5, 6, 7, 8]
# arr1 = set(arr1)
# arr2 = set(arr2)
# arr1.intersection_update(arr2)
# arr1

# # %%
# chars = ['a', 'b', 'c', 'a', 'd', 'b', 'e']
# set([i for i in chars if chars.count(i)<=1])

# # %%


# ##############################################

# # %% [markdown]
# # ### Python program to sort Python Dictionaries by Keys

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# sort_dict = {}

# # for key in sorted(dict1.keys()):
# #     sort_dict[key] = dict1[key]
# # print(sort_dict)

# for i in sorted(dict1.keys()):
#     sort_dict.update({i:dict1[i]})
# print(sort_dict)

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# dict1.update({11: 'Sachin'})
# dict1

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# d = sorted(dict1.items(),key=lambda x:x[0])
# d

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# d = sorted(dict1.items(),key = lambda x:x[0])


# # %% [markdown]
# # ### Python program to sort Python Dictionaries by Values

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# sort_dict = {}

# # for value in sorted(dict1.values()):
# #     for key in dict1:
# #         if dict1[key] == value:
# #             sort_dict.update({key:value})
# # print(sort_dict)

# for values in sorted(dict1.values()):
#     for key in dict1.keys():
#         if values == dict1[key]:
#             sort_dict.update({key:values})
# print(sort_dict)



# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# d = sorted(dict1.items(),key=lambda x:x[1])

# d= sorted(dict1.items(),key=lambda x:x[1])
# d

# # %% [markdown]
# # ### Patterns

# # %%
# # for i in range(1,5):
# #     for j in range(1,i+1):
# #         print("*",end=' ')
# #     print("\n")
    
# #############3
 
    
# n = 5
# for i in range(1,5):
#     for j in range(1,i+1):
#         print('*',end = ' ')
 
#     print()
    

# # %%
# for i in range(1,5):
#     for j in range(1,i+1):
#         print(i,end=' ')
#     print("\n")
    
# for i in range(1,n):
#     for j in range(i):
        
#         print(i,end = ' ')
#     print()
    


# for i in range(1,n):
#     for j in range(1,i+1):
#         print(i,end = ' ')
        
#     print()

# # %%
# for i in range(1,5):
#     for j in range(1,i+1):
#         print(j,end=' ')
#     print("\n")
    
# for i in range(1,n):
#     for j in range(1,i+1):
#         print(j,end = '')
#     print()

# # %%
# for i in range(1,5):
#     for j in range(1,i+1):
#         print(j,end=' ')
#     for k in range(1,j):
#         print(k,end=' ')
#     print("\n")
    
# for i in range(1,n):
#     for j in range(1,i+1):
#         print(j,end = ' ')
#     for k in range(1,j):
#         print(k,end = ' ')
#     print()

# # %%

    
# for i in range(1,5):
#     for j in range(1,i+1):
#         print(j,end= " ")
#     for k  in range(1,j):
#         print(k,end = " ")
#     print()

# # %% [markdown]
# # ### Print given number is prime or not

# # %%
# # number = int(input("Enter the number"))
# number = 15
# for n in range(2,number):
#     if number % 2 == 0:
#         print(f"Given number {number} is not prime")
#         break;
# else:
#     print(f"Given number {number} is prime number")
        

# # %% [markdown]
# # ### Print prime numbers from given range

# # %%
# start = int(input("Enter the start number "))
# end = int(input("Enter the end number "))
# print(f"Prime numbers from {start} to {end} are ")
# for number in range(start,end):
#     for n in range(2,number):
#         if number % n == 0:
#             break
#     else:
#         print(number)
        
# start = int(input('enter start'))
# end = int(input('enter end'))
# l = []
# for i in range(start,end+1):
#     if i%n ==0:
#         break
#     else:
#         print(number)
#         l = l.append(i)
# print(l)


 



# # %%
# [i for i in range(1,15) if i%2!=0] 

# # %% [markdown]
# # ### List Comprehension

# # %%
# list1 = [n for n in range(1,10)]
# list1

# # %% [markdown]
# # ### Print the number which are divisible by 5

# # %%
# list2 = [n for n in range(1,30) if n % 5 == 0]
# list2

 

# # %% [markdown]
# # ### Print the number which are divisible by 5 and 7

# # %%
# list3 = [n for n in range(1,50) if n % 5 == 0 if n % 7 == 0]
# list3

# # %%
# # [n for n in range(1,50) if n % 5 == 0  and if n % 7 == 0]
# # [n for n in range(1,50) if n % 5 == 0  and n % 7 == 0]
# [i for i in range(1,50) if i % 5 == 0 and i % 7 == 0]

# # %% [markdown]
# # ### Print the number which are divisible by 5 or 7

# # %%
# list3 = [n for n in range(1,50) if n % 5 == 0 or n % 7 == 0]
# list3

# # %% [markdown]
# # ### Make square of given list

# # %%
# # list4 = [2,3,4,5,6,7,8,9]
# # list5 = [n**2 for n in list4]
# # list5
# list4 = [2,3,4,5,6,7,8,9]
# list5 = [n**2 for n in list4]
# list5

# # %%
# my_list = [2, 3, 5, 7, 11]
# squared_list = [x**2 for x in my_list if x%2 != 0] # list comprehension
# # output => [9 , 25 , 49 , 121]
# squared_dict = {  for x in my_list if x%2 != 0}
# print(squared_list)
# print(squared_dict)

# {x:x*2 for x in my_list if x%2==0}

# # %% [markdown]
# # ### Find out fruits starts with a

# # %%
# fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
# [fruit for fruit in fruits if fruit.startswith('a') ]
# [f for f in fruits if f.startswith('a')]

# # %% [markdown]
# # ### Fruits containing a letter

# # %%
# fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
# [fruit for fruit in fruits if 'a' in fruit]

# # %% [markdown]
# # ### Common fruits from both lists

# # %%
# basket = ["apple",'guava','cherry','banana']
# my_fruits = ['apple','kiwi','grapes','banana','guava']
# [fruit for fruit in fruits if fruit in basket]

# # [f for f in my_fruits if f in basket]

# # %% [markdown]
# # ### List multiplication

# # %%
# l1 = [1,2,3,4,5]
# l2 = [5,3,4,8]

# [x*y for x in l1 for y in l2]

# [x*y for x in l1 for y in l2]
# # [i*b for i in l1 for b iin l2]
# [i*b for i,b in zip(l1,l2)]

# # %% [markdown]
# # ### Print 2X2 matrix using list comprehension

# # %%
# [[i*j for i in range(1,4)] for j in range(1,5)]

# [[i]]

# # %% [markdown]
# # ###  Write a program to add items of 2 lists indexwise

# # %%
# L1 = [1,2,3,4,33,44]
# L2 = [-11,-20,-63,4,7,22]

# # [i+j for i,j in zip(L1,L2)]
# [i+j for i,j in zip(L1,L2)]
# [i+j for i,j in zip(L1,L2)]

# [i+j for i,j in zip(L1,L2)]



# # %%

# list(zip(L1,L2))

# # %% [markdown]
# # ### Write a program to replace an item with a different item if found in the list 
# # 

# # %%
# L = [5,1,2,3,4,5,311]
# # for number in L:
# #     if number == 5:
# #         L[L.index(number)] = 700
        
# # for i in L:
# #     if i == 5:
        
# #         L[L.index(i)]= 300
        
# ind = L.index(5)
# for i in L:
#     if  i== 5:
#         ind = L.index(5)
#         L[ind] = 100
# L

# # %%
# L = [1,2,3,4,5,311]
# # replace 5 with 300
# # index = L.index(5)
# # L.pop(index)
# # L.insert(index,300)

# index1 = L.index(5)
# L.pop(index1)
# L.insert(index1,400)
# L

# # %%
# L = [1,2,3,4,5,311]
# # replace 3 with 300
# index = L.index(5)
# L[index] = 800
# L[index] = 100
# L

# # %% [markdown]
# # ### Write a program that can convert a 2D list to 1D list

# # %%
# List = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
# for sublist in List:
#     for number in sublist:
#         print(number)
        
# # [i for j in List for i in j ]
# l= []
# for i in List:
#     for j in i:
#         l.append(j)
# l

# [i for j in List for i in j]
# # [number for sublist in List for number in sublist]

# # %%
# [number for sublist in List for number in sublist]

# # %%
# L = [1,2,1,2,3,4,5,3,4]
# temp_list = []

# for number in L:
#     if number  not in temp_list:
#         temp_list.append(number)
# print(temp_list)

# list(set(L))

# temp = []
# for i in L:
#     if i not in temp:
#         temp.append(i)
        
# temp


# # %% [markdown]
# # ### Write a program to remove duplicate items from a list

# # %%
# # L = [1,2,1,2,3,4,5,3,4]
# # temp_list = []

# # for number in L:
# #     if number  not in temp_list:
# #         temp_list.append(number)
# # print(temp_list)

# # list(set(L))

# # temp = []
# # for i in L:
# #     if i not in temp:
# #         temp.append(i)
        
# # temp

# temp_list = []
# L = [1,2,1,2,3,4,5,3,4]
# for i in L:
#     if i in temp_list:
#         pass
#     else:
#         temp_list.append(i)
# temp_list

# # %%
# L = [1,2,1,2,3,4,5,3,4]
# list(set(L))

# # %% [markdown]
# # ### Write a program to check if a list is in ascending order or not

# # %%
# L = [1, 2, 3, 5, 7, 8]

# sorted_flag = ''

# # for i in range(1, len(L)):
# #     if L[i] < L[i - 1]:
# #         sorted_flag = False
# #         break

# # if sorted_flag:
# #     print("List is in ascending order.")
# # else:
# #     print("List is not in ascending order.")
    

# for i in range(1,len(L)):
#     if L[i]<l[i-1]:
#         sorted_flag = False
#         print('no')
#     else:
#         print('sorted')
#         sorted_flag = True
# print(sorted_flag)

# # %%
# L = [1, 2, 3, 15, 7, 8]

# sorted_flag = True

# for i in range(1, len(L)):
#     if L[i] < L[i - 1]:
#         sorted_flag = False
#         break

# if sorted_flag:
#     print("List is in ascending order.")
# else:
#     print("List is not in ascending order.")

# # %%
# L = [1, 2, 3, 5, 7, 8]
# L == sorted(L)

# # %%
# # def is_ascending_order(arr):
# #     for i in range(len(arr) - 1):
# #         if arr[i] > arr[i + 1]:
# #             return False
# #     return True

# # # Example usage:
# # my_list = [1, 2, 73, 4, 5]
# # if is_ascending_order(my_list):
# #     print("The list is in ascending order.")
# # else:
# #     print("The list is not in ascending order.")
    
# def is_ascending(arr):
#     print(arr)
#     if i in range(len(arr)-1):
#         if arr[i] < arr[i+1]:
#             return True
#         else:
#             return False
        
        
# arr = [1,4,2]

# c = is_ascending(arr)
# if c == True:
#     print('ascending')
# else:
#     print('No')


# # %%
# num = int(input('sachin number sang be   '))

# if num%2 == 0:
#     print('this in not prime')
# else: 
#     print('prime')
    



# # %% [markdown]
# # ### Print tuple with number and its square

# # %%
# L1 = [1,2,3,4,5,6,7,8,9]
# [(i,i**2) for i in L1]

# # %%
# {i:i**2 for i in L1}

# # %% [markdown]
# # ### Sort the given list    

# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11]

# for i in range(len(L1)):
#     for j in range(0,len(L1)-1-i):
#         if L1[j] <= L1[j +1]:
#             L1[j], L1[j+1] = L1[j+1],L1[j]
# print(L1)


# l = sorted(L1)


# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11]
# L1.sort()
# L1

# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11]

# result = []

# # while L1:
# #     smallest = min(L1)
# #     result.append(smallest)
# #     L1.remove(smallest)

# # print(result)

# res= []
# for i in L1:
#     smallest = min(L1)
#     res.append(smallest)
#     L1.remove(smallest)
# print(res)

# # %% [markdown]
# # ### Find give number is armstrong number or not in python

# # %%
# number = 124
# temp = number
# cube = 0

# while number > 0:
#     rem = number % 10
#     cube += rem**3
#     number = number // 10

# if cube == temp:
#     print(f'Given number {temp} is armstrong number')
# else:
#     print(f'Given number {temp} is not armstrong number')

# # %%
# # 153 = 1**3+5**3+3**3
# num = 9473 #9474 #153
# def is_amstrong(num):

#     lenght= (len(str(num)))

#     final = 0
#     for i in range(0,lenght):
#     #     print(i)
#         no = int(str(num)[i])

#         final += no**lenght
        
#     if final == num:
#         return True
#     else:
#         return False
    
# res = is_amstrong(num)
# if res == True:
#     print('amstrong')
# else:
#     print('NOOO')



# # if num == 

# # %%
# given_number = 153
# temp = str(given_number)

# cube = 0

# for number in temp:
    
#     cube += int(number) **3
    
# if cube == given_number:
#     print(f'Given number {given_number} is armstrong number')
# else:
#     print(f'Given number {given_number} is not armstrong number')

# # %% [markdown]
# # ### Reverse a given list

# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11]
# # temp_list = []

# # for index in range(len(L1)-1,-1,-1):
# #     temp_list.append(L1[index])
    
# # print(temp_list)
# temp_list = []
# for i in range(len(L1)-1,-1,-1):
#     temp_list.append(L1[i])
# print(temp_list)

# L1[::-1]

# L1.reverse()

# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11]
# L1.reverse()
# L1

# # %%
# # Reverse a list in same list
# list1 = [22,44,55,33,88,99,77]

# for i in range(len(list1)//2):
#     list1[i],list1[len(list1)-1-i] =  list1[len(list1)-1-i],list1[i]
    
# print(list1)

# # %% [markdown]
# # ### Find out the number divisible by 5 and 7

# # %%
# L = [5,23,15,30,45,60,10,35,70]
# [number for number in L if number%5==0 and number%7==0]

# # %%
# L = [5,23,15,30,45,60,10,35,70]
# output = lambda list2 : [number for number in list2 if number%5==0 and number%7==0]
# output(L)

# o = lambda list2 : [i for i in list2 if i%5==0]
# o(l)

# # %%
# list(filter(lambda number: number%5==0 and number%7==0,L))

# # %%
# L = [5,23,15,30,45,60,10,35,70]
# list(filter(lambda i: i%2!=0,L))
# list(filter(lambda i:i%2 !=0,L))

# # %%
# list(filter(lambda number : number%5==0,L))

# # %% [markdown]
# # ### Make square of all numbers from given list

# # %%
# L = [5,23,15,30,45,60,10,35,70]
# [number**2 for number in L]

# # %%
# L = [5,23,15,30,45,60,10,35,70]
# square = lambda L : [number **2 for number in L]
# square(L) 

# # %%
# L = [5,23,15,30,45,60,10,35,70]
# list(map(lambda number : number**2,L))
# list(map(lambda number:number**2,L))

# # %% [markdown]
# # ### Decorator function

# # %%
# # Define a decorator function
# def my_decorator(func):
#     def wrapper():
#         print("Something is happening before the function is called.")
#         func()  # Call the original function
#         print("Something is happening after the function is called.")
#     return wrapper

# # Use the decorator to modify a function
# @my_decorator
# def say_hello():
#     print("Hello!")

# # Call the decorated function
# say_hello()

# # %%


# # %%
# # decorator function to capitalize names
# def names_decorator(function):
#     def wrapper(arg1, arg2):
#         arg1 = arg1.capitalize()
#         arg2 = arg2.capitalize()
#         string_hello = function(arg1, arg2)
#         return string_hello
#     return wrapper

# @names_decorator
# def say_hello(name1, name2):
#     return 'Hello ' + name1 + '! Hello ' + name2 + '!'
# say_hello('sara', 'ansh') 

# # %% [markdown]
# # ### Shallow copy

# # %% [markdown]
# # Shallow Copy:
# # A shallow copy creates a new object, but it only copies the references to the objects contained within the original object, rather than recursively copying the entire contents. This means that changes made to objects inside the copied object will affect both the original and the copy if those objects are mutable.
# # 
# # You can create a shallow copy using the copy.copy() function from the copy module.

# # %%
# import copy

# original_list = [[1, 2, 3], [4, 5, 6]]
# shallow_copy_list = copy.copy(original_list)

# # Modify an element inside the copied list
# shallow_copy_list[0][0] = 100

# # Check the original list
# print(original_list)  # Output: [[100, 2, 3], [4, 5, 6]]
# print(shallow_copy_list)

# # %% [markdown]
# # ### Deep copy

# # %% [markdown]
# # Deep Copy:
# # A deep copy creates a completely independent copy of the original object, including all nested objects. Changes made to objects inside the copied object will not affect the original object.
# # 
# # You can create a deep copy using the copy.deepcopy() function from the copy module.

# # %%
# import copy

# original_list = [[1, 2, 3], [4, 5, 6]]
# deep_copy_list = copy.deepcopy(original_list)

# # Modify an element inside the copied list
# deep_copy_list[0][0] = 100

# # Check the original list
# print(original_list)  # Output: [[1, 2, 3], [4, 5, 6]]
# print(deep_copy_list)

# # %% [markdown]
# # ### Functools reduce

# # %%
# # In Python, the reduce function is part of the functools module and is used for aggregating a sequence (e.g., a list) 
# # of values into a single cumulative result. It repeatedly applies a given function to the elements of the sequence, 
# # accumulating the result.

# import functools

# # Define a function to multiply two numbers
# def multiply(x, y):
#     return x * y

# # Define a list of numbers
# numbers = [1, 2, 3, 4, 5]

# # Use the reduce function to find the product of all elements in the list
# result = functools.reduce(multiply, numbers)

# print(result)  # Output: 120 (1 * 2 * 3 * 4 * 5)


# # %%
# import functools

# # Define a function to multiply two numbers
# def multiply(x, y):
#     return x * y

# # Define a list of numbers
# numbers = [1, 2, 3, 4, 5]

# # Use the reduce function to find the product of all elements in the list
# result = functools.reduce(multiply, numbers)

# print(result)  

# import functools
# res = functools.reduce(multiply,numbers)

# # %% [markdown]
# # ### any() all()

# # %%
# # Example 1: Using any() with a list of boolean values
# bool_values = [True, False, True, False]
# result = any(bool_values)
# print(result)  # Output: True (At least one True value is present)

# # Example 2: Using any() with a list of numbers
# numbers = [0, -1, 4, 7]
# result = any(numbers)
# print(result)  # Output: True (At least one non-zero number is present)

# # Example 3: Using any() with an empty list
# empty_list = []
# result = any(empty_list)
# print(result)  # Output: False (The iterable is empty)


# # %%
# bool_values = [True, False, True, False]
# result = all(bool_values)
# print(result)  # Output: False (At least one True value is present)
# # Example 2: Using any() with a list of numbers
# numbers = [0, -1, 4, 7]
# result = all(numbers)
# print(result)  # Output: False (At least one non-zero number is present)

# # Example 3: Using any() with an empty list
# empty_list = []
# result = all(empty_list)
# print(result)  # Output: True (The iterable is empty)

# # %%
# import re
# import string
# from bs4 import BeautifulSoup
# from nltk.corpus import stopwords

# def process_text(text):
#     # Remove HTML tags using BeautifulSoup
#     text = BeautifulSoup(text, 'html.parser').get_text()
    
#     # Remove numbers using regular expression
#     text = re.sub(r'\d', '', text)
    
#     # Remove special characters using regular expression
#     text = re.sub(r'[' + re.escape(string.punctuation) + ']', '', text)
    
#     # Remove multiple spaces and tabs
#     text = re.sub(r'\s+', ' ', text)
    
#     # Remove words with length less than 3 characters
#     words = text.split()
#     text = ' '.join([word for word in words if len(word) >= 3])
    
#     # Remove common English stopwords
#     stop_words = set(stopwords.words('english'))
#     words = text.split()
#     text = ' '.join([word for word in words if word.lower() not in stop_words])
    
#     # Remove words containing numbers
#     words = text.split()
#     text = ' '.join([word for word in words if not any(char.isdigit() for char in word)])
    
#     # Remove multiple lines using regular expression
#     text = re.sub(r'\n+', '\n', text)
    
#     return text

# # Example usage:
# input_text = "Sachin This is an <b>example</b> text with 123 numbers and some        <a href='#'>HTML tags</a>.\nIt has special characters, stopwords, and short words 67890 ^&%$#."
# processed_text = process_text(input_text)
# print(processed_text)


# # %%
# import re
# import string
# from bs4 import BeautifulSoup
# from nltk.corpus import stopwords

# def remove_numbers(text):
#     # Remove numbers using regular expression
#     return re.sub(r'\d', '', text)

# def remove_html_tags(text):
#     # Remove HTML tags using BeautifulSoup
#     soup = BeautifulSoup(text, 'html.parser')
#     return soup.get_text()

# def remove_special_characters(text):
#     # Remove special characters using regular expression
#     return re.sub(r'[' + re.escape(string.punctuation) + ']', '', text)

# def remove_multiple_spaces_and_tabs(text):
#     # Replace multiple spaces and tabs with a single space
#     return re.sub(r'\s+', ' ', text)

# def remove_words_less_than_3_chars(text):
#     # Remove words with a length less than 3 characters
#     words = text.split()
#     filtered_words = [word for word in words if len(word) >= 3]
#     return ' '.join(filtered_words)

# def remove_stopwords(text):
#     # Remove common English stopwords
#     stop_words = set(stopwords.words('english'))
#     words = text.split()
#     filtered_words = [word for word in words if word.lower() not in stop_words]
#     return ' '.join(filtered_words)

# def remove_words_with_numbers(text):
#     # Remove words containing numbers
#     words = text.split()
#     filtered_words = [word for word in words if not any(char.isdigit() for char in word)]
#     return ' '.join(filtered_words)

# def remove_multiple_lines(text):
#     # Remove multiple lines using regular expression
#     return re.sub(r'\n+', '\n', text)

# def apply_text_processing(text):
#     text = remove_numbers(text)
#     text = remove_html_tags(text)
#     text = remove_special_characters(text)
#     text = remove_multiple_spaces_and_tabs(text)
#     text = remove_words_less_than_3_chars(text)
#     text = remove_stopwords(text)
#     text = remove_words_with_numbers(text)
#     text = remove_multiple_lines(text)
#     return text

# # Example usage:
# input_text = "Sachin             This is an <b>example</b> text with 123 numbers and some <a href='#'>HTML tags</a>.\nIt has special characters, stopwords, and short words 67890 ^&%$#."
# processed_text = apply_text_processing(input_text)
# print(processed_text)


# # %% [markdown]
# # ## Fibonacci number

# # %%
# # Function for nth fibonacci number 
# # Write a program to print fibonacci series upto n terms in python
# num = 10
# n1, n2 = 0, 1
# print("Fibonacci Series:", n1, n2, end=" ")
# for i in range(2, num):
#     n3 = n1 + n2
#     n1 = n2
#     n2 = n3
#     print(n3, end=" ")

# print()


# # %%
# # Find out the fabonacci series numbers which are less than 70

# less_than_number = 70

# number1 = 0
# number2 = 1
# number3 = 0
# print('Fibonacci series:', number1, number2, end=" ")

# while number3 < less_than_number:
#     number3 = number1 + number2
#     if number3 < less_than_number:
#         print(number3, end=" ")
#     number1 = number2
#     number2 = number3


# # %%
# l1 = [1,2,3]
# l2 = [2,3,1]
# l1==l2

# # %%
# # def factorial(n):
# #     if n == 0:
# #         return 1

# #     return n * factorial(n - 1)

# # print(factorial(5))

# def fact(n):
#     if n==0:
#         return 1
#     return n * fact(n-1)
# c= fact(5)

# def fact(n):
#     if n==0:
#         return 1
#     return n*fact(n-1)
# c = fact(4)
# c


# # %%
# a = 0
# b = 1

# l = []

# while a < 70:
#     l.append(a)
#     c = a + b
#     a = b
#     b = c

# print(l)

# a= 0
# b = 1
# l = []
# while a<70:
#     l.append(a)
#     c= a+b
#     a=b
#     b=c
    
# a = 0
# b = 1
# l = []

# while a< 70:
#     l.append(a)
#     c = a+b
#     a = b
#     b = c
    
# a = 0
# b = 1
# l = []
# whi

# # %%
# a = 0
# b= 1
# for i in range(10):
#     print(a,end = ' ')
#     c = a+b
#     a=b
#     b=c

# # %%
# a = 0
# b= 1
# for i in range(10):
#     print(a,end = ' ')
#     c = a+b
#     a=b
#     b=c

# # %%
# a = 0
# b = 1

# for i in range(10):
#     print(a, end=" ")
#     c = a + b
#     a = b
#     b = c

# # %%


# # %%
# def fun():
#     # Initialize variables 'a' and 'b' as strings
#     a = '5'
#     b = '2.5'

#     # Define a nested function 'inc' within 'fun'
#     def inc():
#         # Use nonlocal keyword to access and modify 'a' and 'b' from the outer scope
#         nonlocal a
#         nonlocal b
#         # Convert 'a' to an integer
#         a = int(a)
#         # Convert 'b' to a float
#         b = float(b)
#         # Return the value of 'a'
#         return a

#     # Return the 'inc' function itself, not the result of calling it
#     return inc

# # Call the 'fun' function and assign the returned function to 'c'
# c = fun()
# # Call the function stored in 'c' and print its result
# print(c())

# # %%

# def my_interview(func):
#     def say_hi(name):
#         print('before the interview')
#         func(name)
#     return say_hi
# @my_interview
# def greet(name):
#     print(f'you are taking interview thank  you {name}')
# greet('sachin')


# def my_interview(func):
#     def say_hi(name):
#         print('in the interview')
#         func(name)
        
#     return say_hi
# @my_interview
# def greet(name):
#     print(f'your {name} thank ')
    
# greet('sachin')

# # %%
# def factorial(n):
#     if n == 0 or n == 1:
#         return 1
#     return n * factorial(n - 1)

# num = int(input("Enter a number: "))
# print("Factorial =", factorial(num))

# def factoria(num):
#     if num ==0 or num == 1:
#         return 1
#     return num * factoria(num-1)
    
# c  = factoria(4)
# c
    
    

# # %%
# n = int(input("Enter a number: "))

# fact = 1

# for i in range(1, n + 1):
#     fact = fact * i

# print("Factorial =", fact)
# n = 4
# fact = 1
# for i in range(1,n+1):
#     fact = fact *i
# fact    

# # %%
# def numbers():
#     for i in range(5):
#         yield i

# for i in numbers():
#     print(i)
    
# print(numbers)

# def numbers():
#     for i in range(5):
#         yield i
# for i in numbers():
#     print(i)

# # %%
# def numbers():
#     print("One")
#     yield 1

#     print("Two")
#     yield 2
 
    
# g = numbers()

# print(next(g))
# print(next(g))
# print(next(g))

# # %%
# # g = numbers()

# print(next(g))    

# # %%
# nums = [10, 20, 30,40]

# it = iter(nums)

# print(next(it))
# print(next(it))
# print(next(it))

# num = [1,2,4]
# # it = iter(nums)
# print(next(it))
# print(next(it))

# # %%
# class Animal:
#     def eat(seif):
#         return 'eating'
# class dog(Animal):
#     def bark(self):
#         return 'bark'
    
# d = dog()
# print(d.eat())
# d.bark()

# # %%



# ############################################33333
# # %% [markdown]
# # # OOP

# # %%
# # Simple class

# class Candidate:

#     def __init__(self, name, skill, result):
#         self.name = name
#         self.skill = skill
#         self.result = result

#     def show(self):
#         print(f"Name   : {self.name}")
#         print(f"Skill  : {self.skill}")
#         print(f"Result : {self.result}")


# ashu = Candidate("Ashwini", "LLM", "Selected")

# ashu.show()

# # %%
# sach = Candidate("sachin", "QA", "Selected")
# sach.show()

# # %%
# # Calculator

# class Calculater:
 
#     def add(self,a,b):
#         return a+b
#     def sub(self,a,b):
#         return a-b
    
# cal = Calculater()
# print(cal.add(10,5))
# print(cal.sub(10,5))

# # %%
# class Calculator:

#     def add(self, a, b):
#         return a + b

#     def subtract(self, a, b):
#         return a - b

#     def multiply(self, a, b):
#         return a * b

#     def divide(self, a, b):
#         if b == 0:
#             return "Cannot divide by zero"
#         return a / b


# calc = Calculator()

# print("Addition:", calc.add(10, 5))
# print("Subtraction:", calc.subtract(10, 5))
# print("Multiplication:", calc.multiply(10, 5))
# print("Division:", calc.divide(10, 5))

# # %%
# #instance method  # classs methos # satatic methood

# class Employee:

#     company = "Amdocs"

#     def __init__(self, name):
#         self.name = name

#     # Instance Method
#     def employee_info(self):
#         print(self.name, self.company)

#     # Class Method
#     @classmethod
#     def change_company(cls, company):
#         cls.company = company

#     # Static Method
#     @staticmethod
#     def is_adult(age):
#         return age >= 18


# e1 = Employee("Ashwini")
# e2 = Employee("Sachin")

# e1.employee_info()
# e2.employee_info()

# Employee.change_company("Google")

# e1.employee_info()
# e2.employee_info()

# print(Employee.is_adult(25))

# # %%
# # Super
# class mother:

#     def __init__(self):
#         print("mother sari")


# class daughter(mother):

#     def __init__(self):
       
#         print("daughter sari")


# d = daughter()

# # %%
 

# # Super
# class mother:

#     def __init__(self):
#         print("mother sari")


# class daughter(mother):

#     def __init__(self):
        
#         super().__init__()
       
#         print("daughter sari")


# d = daughter()

# # %%
# # inheritance 

# class Animal:
#     def sound(self):
#         print('sound\n')
# class Dog(Animal):
#     def bark(self):
#         print(f' dog ')
# d = Dog()
# d.sound()
# d.bark()



# # %%
# #polymorphism

# class Animal:
#     def sound(self):
#         print("Animal makes a sound")


# class Dog(Animal):
#     def sound(self):
#         print("Dog barks")


# class Cat(Animal):
#     def sound(self):
#         print("Cat meows")


# Dog().sound()
# Cat().sound()

# # %%
# #method overridding
# class Animal:
#     def sound(self):
#         print("Animal makes a sound")


# class Dog(Animal):
#     def sound(self):
#         print("Dog barks")


# class Cat(Animal):
#     def sound(self):
#         print("Cat meows")


# Dog().sound()
# Cat().sound()

# # %%
# # method overloading

# class Calculator:

#     def add(self, a, b, c=0):
#         return a + b + c


# cal = Calculator()

# print(cal.add(10, 20))
# print(cal.add(10, 20, 30))

# # %%
# # abstrctiosn

# from abc import ABC, abstractmethod

# class Animal(ABC):

#     @abstractmethod
#     def sound(self):
#         pass


# class Dog(Animal):

#     def sound(self):
#         print("Bark")


# dog = Dog()
# dog.sound()

# # %%
# # emcapsulation

# class Employee:

#     def __init__(self):
#         self.name = "Ashwini"        # Public
#         self._department = "AI"      # Protected
#         self.__salary = 200000       # Private


# emp = Employee()

# print(emp.name)          # Public
# print(emp._department)   # Protected (works, but not recommended)
# print(emp.__salary)    # Error

# # %%


# # %%
# # decorator

# def my_interview(func):
#     def technical(name):
        
#         print('passed')
#         func(name)
#         print('happy')
#     return technical
# @my_interview
# def result(name):
#     print(f'{name} selected')
# result('ashwini')



# # %%
# class Solution(object):
#     def twoSum(self, nums, target):
#         s = nums+target
#         """
#         :type nums: List[int]
#         :type target: int
#         :rtype: List[int]
#         """
#         return s

# d =Solution()
# k =d.twoSum(2,3)
# k

# # %%



# ############################################################3
# # %%


# # %%
# import pandas as pd
 

# # ===========================================================
# # PANDAS LEVEL 1 - BASICS
# # ===========================================================

# # -----------------------------------------------------------
# # 1. Create DataFrame from Dictionary
# # -----------------------------------------------------------

# data = {
#     "EmpID": [101, 102, 103, 104, 105],
#     "Name": ["Alice", "Bob", "Charlie", "David", "Eva"],
#     "Age": [25, 30, 35, 28, 26],
#     "Department": ["HR", "IT", "Finance", "IT", "HR"],
#     "Salary": [50000, 70000, 80000, 65000, 55000],
#     "City": ["Pune", "Mumbai", "Delhi", "Bangalore", "Pune"]
# }

 

# df =pd.DataFrame(data)
# df

# # %%
# type(df)

# # %%
# df.shape

# # %%
# df.head(2)

# # %%
# df.tail(2)

# # %%
# df.columns

# # %%
# df.columns.tolist()
 

# # %%
# df.index

# # %%
# df.info()

# # %%
# df.describe()

# # %%
# df.describe(include='all')
 

# # %%
# df['Name']

# # %%
# df.columns

# # %%
# df[['Name','Age']]


# # %%
# df.iloc[0]

# # %%
# df.iloc[2]

# # %%
# df.iloc[0:2]

# # %%
# df.loc[0]

# # %%
# df.loc[0:2]

# # %%
# df.loc[0,'Name']

# # %%
# df.iloc[0:2] # slicing end excluded

# # %%
# df["Bonus"] = [5000, 7000, 8000, 6500, 5500]
# df

# # %%
# df['totak '] = df['Salary'] + df['Bonus']
# df

# # %%
# df.columns

# # %%
# df['totak']  = df['totak '] + 1000000
# df

# # %%
# df.rename(columns={'totak ':'total'},inplace=True)
# df.columns

# # %%
# df

# # %%
# df.rename(columns={'Dept':'new_dpt'},inplace=True)
# df.columns

# # %%

# df.rename(columns={"Department": "Dept"}, inplace=True)

# print("\nRenamed Column")
# print(df)


# # %%
# df.columns

# # %%
# df.drop('totak',axis=1,inplace=True)
# df

# # %%
# d = df.copy()
# d

# # %%
# del d
# d

# # %%
# #  --------------------------------------------------------

# df3 = df.copy()

# removed = df3.pop("City")

# print("\nAfter Pop")
# print(df3)

# print("\nRemoved Column")
# print(removed)


# # %%
# # -----------------------------------------------------------

# df4 = df.copy()

# df4.index = [11, 12, 13, 14, 15]

# print("\nChanged Index")
# print(df4)


# # %%
# df4.reset_index(inplace=True)
 
# df4

# # %%
# df.columns

# # %%
# df[['EmpID', 'Name', 'Age']]

# # %%
# df['Name'].value_counts()

# # %%
# # list(df['Name'].unique())
# (df['Name'].unique()).tolist()

# # %%
# df['Salary'].max()

# # %%
# import pandas as pd
# from ydata_profiling import ProfileReport
# profile = ProfileReport(df)
# profile.to_file("report.html")

# # %%
# df.sort_values('Salary',ascending=True)
# df.sort_values('Salary')
# df.sort_values('Salary')

# # %%
# pd.to_csv('emp.csv',index=False)

# # %%
# d = df[df['Age']>30]
# d

# # %%
# d = df[(df['Age']>30) & (df['Salary']>=80000)]
# d = df[(df['Age']>30)&(df['Salary']>=80000)]
# d

# # %%
# df[df['Age'].isin([30,35])]

# # %%
# df[df['Age'].between(28,38)]

# # %%
# df.query("Age > 30")

# # %%
# df.isnull()

# # %%
# df.isnull().sum()

# # %%
# df.fillna(0)

# # %%
# import numpy as np
# df.loc[2, "Salary"] = np.nan
# df

# # %%
# df = df.fillna(0)
# df


# # %%
# df.duplicated()

# # %%
# df.duplicated().sum()

# # %%
# df.drop_duplicates()

# # %%
# df['Name'].str.lower()


# # %%
# df['Name'].apply(len)

# # %%
# df['Age'].apply(int)

# # %%
# df.columns

# # %%
# df

# # %%
# df["EmpID"].apply(lambda x: x + 1000)
# df

# # %%
# gender = {
#     "Alice": "Female",
#     "Bob": "Male",
#     "Charlie": "Male"
# }
# df['Gender'] = df['Name'].map(gender)

# df["Gender"] = df["Name"].map(gender)
# df

# # %%
# df.replace("HR", "Human Resource")  # wholde df
# df.replace("Human Resource",'HRRRRRRRRRR')

# # %%
# df.replace("Pune",'HRRRRRRRRRR')

# # %%
# df.sample(3)

# df.sample(frac=0.5)
# df

# # %%
# import pandas as pd
# import numpy as np

# data = {
#     "Emp_ID":[101,102,103,104,105,106],
#     "Name":["Alice","Bob","Charlie","David","Eva","Frank"],
#     "Department":["IT","HR","IT","Finance","HR","IT"],
#     "Salary":[60000,45000,70000,50000,48000,80000],
#     "Age":[25,30,35,40,29,32],
#     "City":["Pune","Mumbai","Pune","Delhi","Mumbai","Pune"]
# }

# df = pd.DataFrame(data)

# df

# # %%
# df['Salary'].min()

# # %%
# df['Salary'].median()

# # %%
# df['Salary'].count()

# # %%
# df['Salary'].std()

# # %%
# df.columns

# # %%
# group = df.groupby('Department')
# print(group)

# # %%
# group = df.groupby('Department')
# group.count()

# # %%
# group = df.groupby('Department')['Salary'].sum()
# group

# # %%
# df.groupby("Department")["Salary"].mean()

# # %%
# df.groupby("Department")["Salary"].agg(["sum","mean","max","min","count"])
# df.groupby('Department')['Salary'].agg(['sum','min','max'])

# # %%
# result = df.groupby("Department")["Salary"].min()

# print(result)
# result['HR']

# # %%
# group = df.groupby(['Department','City'])['Salary']
# group.sum()

# # %%
# group = df.groupby('Department')['Salary']
# group.get_group('IT')

# # %%
# df.groupby("Department").size()

# # %%
# df[df["Department"] == "HR"]["Salary"]

# # %%
# df

# # %%
# df1,df2
# df.join(df2,on=['Dpt'])
# df = pd.merge(df1,df2,on=['DRP00'],how = 'inner')

# # %%
# import random

# lst = [random.randint(0, 1) for _ in range(50)]

# print(lst)

# import random
# lst = [random.randint(0,1) for i in range(20)]
# lst

# # %%
# lst = [random.randint(0,100) for i in range(10)]
# lst

# # %%
# #  Find the IDs of products that are both low-fat (low_fats == 'Y') and recyclable (recyclable == 'Y').

# import pandas as pd

# # Sample DataFrame
# products = pd.DataFrame({
#     'product_id': [1, 2, 3, 4],
#     'low_fats': ['Y', 'N', 'Y', 'Y'],
#     'recyclable': ['N', 'Y', 'Y', 'Y']
# })

# condiction =(products['low_fats']=='Y') &(products['recyclable']=='Y')
# res = products[condiction][['product_id']]
# res
# # Code Solution
# # condition = (products['low_fats'] == 'Y') & (products['recyclable'] == 'Y')
# # result = products[condition][['product_id']]
# # print(result)


# # %%
# #  Given an orders dataset, calculate the total revenue generated per product category and sort it in descending order.

# orders = pd.DataFrame({
#     'category': ['Electronics', 'Clothing', 'Electronics', 'Clothing', 'Home'],
#     'total_price': [500, 40, 1200, 80, 150]
# })

# group = orders.groupby(['category'])['total_price'].sum().reset_index().sort_values(by='total_price',ascending = True)
# group

# # %%


# # %%
# #  Compare each employee's salary with the average salary of their corresponding department. The output must contain an additional column for the department's average

# employees = pd.DataFrame({
#     'first_name': ['Alice', 'Bob', 'Charlie', 'David'],
#     'department': ['HR', 'IT', 'IT', 'HR'],
#     'salary': [50000, 80000, 110000, 60000]
# })

# # Code Solution
# employees['dept_avg_salary'] = employees.groupby('department')['salary'].transform('mean')
# print(employees)
 

# # %%
# import pandas as pd

# df = pd.DataFrame({
#     "salary": [30000, 60000, 45000, 80000]
# })

# print(df)

# # %%
# df["flag"] = df["salary"].apply(
#     lambda x: 1 if x > 50000 else 0
# )

# # %%
# def check_salary(x):
#     if x > 50000:
#         return 1
#     else:
#         return 0

# df["flag"] = df["salary"].apply(check_salary)

# # %%
# import pandas as pd

# df = pd.DataFrame({
#     "A": [1,2],
#     "B": [3,4]
# })

# def total(row):
#     return row["A"] + row["B"]

# df["Total"] = df.apply(total, axis=1)

# print(df)


# ######################################################

# # %%
# l = [1,2,3]
# c = [3,5,6]
# l.append(2)
# l


# # %%
# l = [1,2,3]
# c = [3,5,6]
# k = l.extend(c)
# k

# # %%


# # %%
# l = [1,2,3]
# c = [3,5,6]
# l.extend(c)
# l

# # %%
# l.insert(0,1000)
# l

# # %%
# l.count(3)

# # %%
# l.sort()
# print(l)

# # %%
# del l

# # %%
# s = 'sachin'
# s.capitalize()

# # %%
# s = 'sachin'
# s.lower()

# # %%
# s.isspace()

# # %%
# s.split()

# # %%
# t = 1,2
# type(t)

# # %%
# t = (3,)
# type(t)

# # %%
# s = set()
# type(s)

# # %%
# s = {1,2,3}
# type(s)

# # %%
# l = [3,2,5]
# l.sort()
# l

# # %%
# l = [3,2,5]
# c = sorted(l)
# c

# # %%
# sum(l)

# # %%
# l.sum()

# # %%
# l[-1]

# # %%
# L  = ['a','b','c']
# for i,j in enumerate(L):
#     print({i:j})

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# dict1.get(1)

# # %%
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# dict1[1]

# # %%
# dict1 = {3: 'Santosh', 5: 'Shweta', 4: 'Sanjiwani', 2: 'Snehal'}
# dict1.pop(3)
# dict1.popitem()
# dict1

# # %%
# def addd(*a):
    
#     k = 0
#     for i in a:
#         k  +=i
#     return k
# addd(12,35,2)





# # %%
# def addd(**a):

#     for key, value in a.items():
#         print(key, value)


# addd(x=2, y=5)

 

# # %%
# # sort dict by keys
# dict2 = {}
# dict1 = {1:"Sachin",3:"Santosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# for i in sorted(dict1.keys()):
#     dict2.update({i:dict1[i]}
#                 )
# print(dict2)


# # %%
# # sort by values
# dict1 = {1:"Sachin",3:"ntosh",5:"Shweta",4:"Sanjiwani",2:"Snehal",6:"Sujit"}
# j = sorted(dict1.values())
# # print(j)
# dict2 = {}
# for i in j:
#     for k in dict1.items():
# #         print(k)
# #         print(k[1])
#         if  i == k[1]:
# #             print(i)
#             dict2.update({k[0]:k[1]})
# print(dict2)
            
        

# # for values in sorted(dict1.values()):
# #     for key in dict1.keys():
# #         if values == dict1[key]:
# #             sort_dict.update({key:values})
# # print(sort_dict)

 
    


# # %%
# dict1.items()

# # %%


# # %%
# next(iter(dict1.items()))

# # %%
# c= len(dict1.items())
# k =iter(sorted(dict1.items()))

# l = []
# for i in range(c):
#     d = next(k)
 
#     l.append(d)
# l

# # %%
# a = sorted(dict1.items(),key = lambda x:x[0]) # by key 
# a

# # %%
# a = sorted(dict1.items(),key = lambda x:x[1])
# a

# # %%
# # find even /odd number or not
# c = 3
# if c%2==0:
#     print('EVEN')
# else:
#     print('ODD')

# # %%
# n= 11
# if n<=1:
#     print('not prime')
# else:
#     is_prime=True
#     for i in range(2,n):
#         if n%i==0:
#             is_prime=False
#             break
#         else:
             
#             is_prime=True
#     if is_prime ==True:
#         print('prime')
#     else:
#         print(' not prime')

        

# # %%
# [i for i in range(1,16)]

# # %%
# [i for i in range(1,16) if i%2==0]

# # %%
# [i for i in range(1,16) if (i%3==0) & (i%2==0)]

# # %%

# import math
# math.sqrt(n)

# # %%
# is_prime = lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))

# primes = [n for n in range(1, 51) if is_prime(n)]

# print(primes)

 

# # %%
# is_prime = lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))
 
 
# primes = list(filter(is_prime, range(1, 51)))

# print(primes)

# # %%
# [i*i for i in primes]

# # %%
# dict1 = [{i:i*i} for i in primes]
# dict2 = [{i:i*8} for i in primes if i %2 ==0]
# dict2

# # %%
# sen = 'Python and data'
# c = sen.split('and')
# c

# # %%
# fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
# [fruit for fruit in fruits if fruit.startswith('a')]

# # %%
# c = lambda i:i.upper()
# list(map(c,fruits))

# # %%
# c = lambda i:i.startswith('c')
# list(filter(c,fruits))

# # %%
# basket = ["apple",'guava','cherry','banana']
# my_fruits = ['apple','kiwi','grapes','banana','guava']
# [f for f in my_fruits if f in basket]

# # %%
# l1 = [1,2,3,4,5]
# l2 = [5,3,4,8]
# [i*j for i,j in zip(l1,l2)]

# # %%
# matrix = [[0 for j in range(2)] for i in range(2)]

# print(matrix)

# # %%
# matrix = [[0 for _ in range(2)] for i in range(2)]

# print(matrix)

# # %%
# matrix = [[5 for j in range(2)] for i in range(2)]

# print(matrix)

# # %%
# # Write a program to replace an item with a different item if found in the list
# L = [5,1,2,3,4,5,311]
# n = 5
# c= []
# for i in L:
#     print('_______ ',i)
#     if i ==5:
       
#         ind = L.index(i)
#         print(ind)
#         L.pop(ind)
# #         print(L)
#         L.insert(ind,300)
#         print(L)
#     else:
#         pass
        
# L

# # %%
# # Write a program to check if a list is in ascending order or not
# L = [51, 2, 3, 5, 7, 8]
# is_asc = True
# for i in range(0,len(L)-1):
 
#     if L[i] >L[i+1]:
      
#         is_asc = False
#         break
#     else:
#         is_asc = True
# if is_asc:
#     print('yes')
# else:
#     print('no')

# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11]
# asc = []
# l = []
# print(L1)
# for i in range(len(L1)):
#     c = min(L1)
    
#     asc.append(c)
#     ind = L1.index(c)
#     L1.remove(c)
# print(asc)

# # %%
# # Find give number is armstrong number or not in python
# n = 9474
# c = str(n)
 
# length = len(str(n))
# count = 0

# for i in range(0,len(str(n))):
# #     print(i)
#     j = int(c[i])
#     count += j**length
# if count == n:
#     print('yes')
# else:
#     print('no')

# # %%
# L1 = [4,55,1,77,3,2,88,77,44,22,11] # reverse the list
# L = []

# for i in range(len(L1)-1,-1,-1):
#     L.append(L1[i])
# print(L)


# # %%
# [i*2 for i in L]

# # %%
# import functools
# def mul(a,b):
#     return a*b
# l = [11,2,3]

# c = lambda x,y:x*y

# res = functools.reduce(c,l)
# res = functools.reduce(mul,l)
# res


# # %%
# import re
# import string
# from bs4 import BeautifulSoup
# from nltk.corpus import stopwords

# def process_text(text):
#     # Remove HTML tags using BeautifulSoup
#     text = BeautifulSoup(text, 'html.parser').get_text()
    
#     # Remove numbers using regular expression
#     text = re.sub(r'\d', '', text)
    
#     # Remove special characters using regular expression
#     text = re.sub(r'[' + re.escape(string.punctuation) + ']', '', text)
    
#     # Remove multiple spaces and tabs
#     text = re.sub(r'\s+', ' ', text)
    
#     # Remove words with length less than 3 characters
#     words = text.split()
#     text = ' '.join([word for word in words if len(word) >= 3])
    
#     # Remove common English stopwords
#     stop_words = set(stopwords.words('english'))
#     words = text.split()
#     text = ' '.join([word for word in words if word.lower() not in stop_words])
    
#     # Remove words containing numbers
#     words = text.split()
#     text = ' '.join([word for word in words if not any(char.isdigit() for char in word)])
    
#     # Remove multiple lines using regular expression
#     text = re.sub(r'\n+', '\n', text)
    
#     return text

# # Example usage:
# input_text = "Sachin This is an <b>example</b> text with 123 numbers and some        <a href='#'>HTML tags</a>.\nIt has special characters, stopwords, and short words 67890 ^&%$#."
# processed_text = process_text(input_text)
# print(processed_text)


# # %%
# a= 0

# b = 1
# l = []
# while a<70:
#     l.append(a)
#     c= a+b
#     a=b
#     b=c
    
# l

# # %%
# n = 4

# def fact(n):
#     if n==0 or n==1:
#         return 1
#     else:
    
#         return n*fact(n-1)
# fact(n)

# # %%
# def numbers():
#     for i in range(5):
#         yield i

# # for i in numbers():
# #     print(i)
    
# g =numbers()
# print(next(g))
 
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))

# # %%
# l = [1,2,3]
# c = iter(l)
# next(c)

# # %%
# next(c)

# # %%
# c = '1+8'
# print(eval(c))

# # %%
# import ast

# x = ast.literal_eval("[1,2,3]")

# print(x)

# # %%
# type(x)

# # %%
# a = '[1,2]'
# import ast
# x = ast.literal_eval(a)
# type(x)

# # %%
# with open('abc.txt','r') as f:
#     print(f.read())

# # %%
# f = open('abc.txt','r'):
# print(f.read())
# f.close()
    

# # %%
# f = open('mode.pkl','wb')
# pickle.dump(model,f)
# f.close

# f = open('model.pkl','rb')
# m = pickle.load(f)
# m.close()

# # %%
# file_dir = r''
# file_path =os.list_dir(file_dir)
# for i in file_path:
#     if i.endswith('.txt'):
#         print(i)
        
# os.path.join(curent_path,file_path)

# # %%
# import datetime
# import time

# start = time.time()
# for i in range(1,100):
#     print(i,end = ' ')
# end = time.time()
# time_r = end-start
# print()
# print(time_r)

# # %%
# print('hi')
# time.sleep(3)
# print('hi')

# # %%
# today = datetime.datetime.now()
# datetime.datetime.today()

# # %%
# datetime.datetime.today().year

# # %%
# datetime.datetime.today().hour

# # %%
# import time
# import datetime

# current= datetime.datetime.today()
# delta = current + datetime.timedelta(days = -2)
# delta

# # %%
# n , i = zip(('ash','sach'))
# print(n)
# print(i)


# # %%


# # %%
# l1 = [1,2,3]
# l2 = [4,5,6]
# l = zip(l1,l2)
# l
# for i, j in l:
#     print(i,j)

# # %%
# import json

# student = {
#     "name": "Alice",
#     "marks": 95
# }

# # Python object -> JSON string
# json_str = json.dumps(student)

# # JSON string -> Python object
# student2 = json.loads(json_str)

# # Python object -> File
# with open("student.json", "w") as f:
#     json.dump(student, f)

# # File -> Python object
# with open("student.json", "r") as f:
#     student3 = json.load(f)

# print(json_str)
# print(student2)
# print(student3)

# # %%
# class comp:
#     def config(self):
#         print('15')
# c = comp()
# c.config()

# # %%
# comp.config()

# # %%
# comp.config(c)

# # %%
# class comp:
#     def config(this):
#         print('15')
# c = comp()
# c.config()

# # %%
# class comp:
#     def config(check):
#         print('15')
# c = comp()
# c.config()

# # %%



# #######################################################
# # %%
# import re
# import string
# from bs4 import BeautifulSoup
# from nltk.corpus import stopwords

# def remove_numbers(text):
#     # Remove numbers using regular expression
#     return re.sub(r'\d', '', text)

# def remove_html_tags(text):
#     # Remove HTML tags using BeautifulSoup
#     soup = BeautifulSoup(text, 'html.parser')
#     return soup.get_text()

# def remove_special_characters(text):
#     # Remove special characters using regular expression
#     return re.sub(r'[' + re.escape(string.punctuation) + ']', '', text)

# def remove_multiple_spaces_and_tabs(text):
#     # Replace multiple spaces and tabs with a single space
#     return re.sub(r'\s+', ' ', text)

# def remove_words_less_than_3_chars(text):
#     # Remove words with a length less than 3 characters
#     words = text.split()
#     filtered_words = [word for word in words if len(word) >= 3]
#     return ' '.join(filtered_words)

# def remove_stopwords(text):
#     # Remove common English stopwords
#     stop_words = set(stopwords.words('english'))
#     words = text.split()
#     filtered_words = [word for word in words if word.lower() not in stop_words]
#     return ' '.join(filtered_words)

# def remove_words_with_numbers(text):
#     # Remove words containing numbers
#     words = text.split()
#     filtered_words = [word for word in words if not any(char.isdigit() for char in word)]
#     return ' '.join(filtered_words)

# def remove_multiple_lines(text):
#     # Remove multiple lines using regular expression
#     return re.sub(r'\n+', '\n', text)

# def apply_text_processing(text):
#     text = remove_numbers(text)
#     text = remove_html_tags(text)
#     text = remove_special_characters(text)
#     text = remove_multiple_spaces_and_tabs(text)
#     text = remove_words_less_than_3_chars(text)
#     text = remove_stopwords(text)
#     text = remove_words_with_numbers(text)
#     text = remove_multiple_lines(text)
#     return text

# # Example usage:
# input_text = "Sachin             This is an <b>example</b> text with 123 numbers and some <a href='#'>HTML tags</a>.\nIt has special characters, stopwords, and short words 67890 ^&%$#."
# processed_text = apply_text_processing(input_text)
# print(processed_text)


# # %%
# import re
# import string
# from nltk.corpus import stopwords
# from bs4 import BeautifulSoup

# input_text = "Sachin This is an <b>example</b> text with 123 numbers and some        <a href='#'>HTML tags</a>.\nIt has special characters, stopwords, and short words 67890 ^&%$#."

# input_text 


# # %%
# text = BeautifulSoup(input_text,'html.parser').get_text() 
# text

# # %%
# text = re.sub('\d','',text)
# text

# # %%
# c = text.split()
# ' '.join([i for i in c if len(i)>3])

# # %%
# text

# # %%
# c = text.split() 
# stop = set(stopwords.words('English'))
# ' '.join([i for i in c if i not in stop])


# # %%
# text = re.sub('\n',' ',text)
# text

# # %%
# # # Remove special characters (keep letters, numbers and spaces)
# # text = re.sub(r'[^A-Za-z0-9 ]', '', text)

# # # Remove words containing numbers
# # result = " ".join(word for word in text.split() if word.isalpha())

# # %%
# text

# # %%
# # text = re.sub(r'[^A-Za-z0-9]',' ',text)
# # text = re.sub(r'[^A-Za-z0-9]',' ',text)
# # text = re.sub(r'[^a-zA-Z0-9]',' ',text)
# text = ' '.join([i for i in text.split if i.isalpha()])
# text

# # %%


# # %%



l = [4,55,1,77,3,2,88,77,44,22,11]
print(len(l))