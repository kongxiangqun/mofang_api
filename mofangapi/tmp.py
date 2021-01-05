# aa = [4,9,5,3,8,1,0]
# def func(i):
#     if i % 2 != 0:
#         return True
# def func1(a):
#     sort1 = sorted(filter(func,aa))
#     for i in range(len(a)):
#         if a[i] % 2 != 0:
#             a[i] = sort1[0]
#             sort1.pop(0)
#     return a
# res = func1(aa)
# print(res)

a = 'qwetyuip'
c = []
# return ['qw','er','ty','ui']
j = -2
for i in range(len(a)):
    if i % 2 == 0:
        j+=2
    if i % 2 == 1:
        b = a[j:i+1]
        c.append(b)
print(c)

# 1 j=0 i=0 j+=1
# 2 j=1 i=1 i+=1
#
# 3 j=1 i=2 j+=1



