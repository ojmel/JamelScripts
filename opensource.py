import pandas as pd
df = pd.DataFrame({
    'A': [5, 15, 10, 8],
    'B': [20, 3, 7, 12]
})
result =   (df['B'] >= 10) | (df >= 10)
print(df >= 10)
print(df['A'] >= 10)
print(result)