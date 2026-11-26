import random, sys, math, hashlib
random.seed(2)
h = {k: hashlib.sha256() for k in ("f*c", "c*c", "abs", "sqrt", "c/c", "sin", "exp", "log", "atan2", "pow")}
for _ in range(100000):
    z = complex(random.uniform(-5, 5), random.uniform(-5, 5)); y = complex(random.uniform(-5, 5), random.uniform(-5, 5)); x = random.uniform(0.1, 5)
    h["f*c"].update(repr(x * z).encode()); h["c*c"].update(repr(z.conjugate() * y).encode()); h["abs"].update(repr(abs(z) ** 2).encode())
    h["sqrt"].update(repr(math.sqrt(x)).encode()); h["c/c"].update(repr(z / y).encode()); h["sin"].update(repr(math.sin(x)).encode())
    h["exp"].update(repr(math.exp(x)).encode()); h["log"].update(repr(math.log(x)).encode()); h["atan2"].update(repr(math.atan2(z.imag, z.real)).encode())
    h["pow"].update(repr(x ** 0.37).encode())
print(sys.version.split()[0], " ".join(f"{k}:{v.hexdigest()[:8]}" for k, v in h.items()))
