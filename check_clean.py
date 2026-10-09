from preprocess import prepare_text

a = prepare_text("He couldn't say that. Trump's team")
b = prepare_text("He couldn t say that. Trump s team")
print(a)
print(b)
print("Identical:", a == b)