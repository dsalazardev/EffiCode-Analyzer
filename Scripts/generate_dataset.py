import json
import random

# Configuración
OUTPUT_FILE = "large_dataset_cormen.json"
NUM_SAMPLES = 20000  # ¡Aquí defines tus 20k!

# Vocabulario para variaciones
VARS = ['i', 'j', 'k', 'idx', 'counter', 'ptr', 'x', 'y', 'z', 'temp', 'val', 'key', 'aux']
ARRAYS = ['A', 'B', 'C', 'Arr', 'Data', 'List', 'Buffer']
OPS = ['+', '-', '*', 'div', 'mod']

def get_var(): return random.choice(VARS)
def get_arr(): return random.choice(ARRAYS)
def get_op(): return random.choice(OPS)

# --- Generadores de Patrones (Templates) ---

def gen_o_1():
    """Genera algoritmos O(1)"""
    patterns = [
        f"return {get_arr()}[{get_var()}]",
        f"{get_var()} ← {get_var()} {get_op()} 1\nreturn {get_var()}",
        f"if {get_var()} > 0 then\n    return true\nelse\n    return false",
        f"SWAP({get_arr()}, {get_var()}, {get_var()})\n    temp ← {get_arr()}[{get_var()}]\n    {get_arr()}[{get_var()}] ← {get_arr()}[{get_var()}]\n    {get_arr()}[{get_var()}] ← temp",
        f"{get_arr()}[{get_var()}] ← {get_var()}"
    ]
    return random.choice(patterns)

def gen_o_n():
    """Genera algoritmos O(n)"""
    v = get_var()
    arr = get_arr()
    body = random.choice([
        f"    sum ← sum {get_op()} {arr}[{v}]",
        f"    if {arr}[{v}] == key then\n        return {v}",
        f"    {arr}[{v}] ← {arr}[{v}] * 2",
        f"    print({arr}[{v}])"
    ])
    
    patterns = [
        f"for {v} ← 1 to n do\n{body}",
        f"for {v} ← n downto 1 do\n{body}",
        f"{v} ← 0\nwhile {v} < n do\n{body}\n    {v} ← {v} + 1"
    ]
    return random.choice(patterns)

def gen_o_n2():
    """Genera algoritmos O(n^2)"""
    v1 = get_var()
    v2 = get_var()
    while v1 == v2: v2 = get_var() # Asegurar variables distintas
    arr = get_arr()
    
    body = random.choice([
        f"        {arr}[{v1}][{v2}] ← {v1} + {v2}",
        f"        if {arr}[{v2}] < {arr}[{v2}-1] then\n            SWAP({arr}, {v2}, {v2}-1)",
        f"        sum ← sum + {arr}[{v1}] * {arr}[{v2}]"
    ])
    
    patterns = [
        f"for {v1} ← 1 to n do\n    for {v2} ← 1 to n do\n{body}",
        f"for {v1} ← 1 to n do\n    for {v2} ← {v1} to n do\n{body}", # Triangular
        f"for {v1} ← 1 to n - 1 do\n    for {v2} ← n downto {v1} + 1 do\n{body}" # Estilo Bubble
    ]
    return random.choice(patterns)

def gen_o_log_n():
    """Genera algoritmos O(log n)"""
    v = get_var()
    patterns = [
        f"while {v} > 1 do\n    {v} ← {v} div 2",
        f"i ← 1\nwhile i < n do\n    i ← i * 2",
        f"BINARY-SEARCH({get_arr()}, 1, n, key)\n    low ← 1\n    high ← n\n    while low ≤ high do\n        mid ← (low + high) div 2\n        if {get_arr()}[mid] == key then return mid\n        else if {get_arr()}[mid] < key then low ← mid + 1\n        else high ← mid - 1"
    ]
    return random.choice(patterns)

def gen_o_n3():
    """Genera algoritmos O(n^3) - Matrices"""
    v1, v2, v3 = random.sample(VARS, 3)
    arr = get_arr()
    return f"for {v1} ← 1 to n do\n    for {v2} ← 1 to n do\n        for {v3} ← 1 to n do\n            {arr}[{v1}][{v2}] ← {arr}[{v1}][{v3}] * {arr}[{v3}][{v2}]"

def gen_o_2n():
    """Genera algoritmos O(2^n) - Recursivos"""
    func_name = random.choice(['SOLVE', 'FIB', 'HANOI', 'SUBSETS'])
    return f"{func_name}(n)\n    if n ≤ 1 then return n\n    return {func_name}(n-1) + {func_name}(n-2)"

# --- Motor Principal ---

def generate_dataset(num_samples):
    dataset = []
    print(f"Generando {num_samples} algoritmos sintéticos...")
    
    # Distribución aproximada
    counts = {
        'O(1)': int(num_samples * 0.1),
        'O(log n)': int(num_samples * 0.15),
        'O(n)': int(num_samples * 0.3),
        'O(n^2)': int(num_samples * 0.3),
        'O(n^3)': int(num_samples * 0.05),
        'O(2^n)': int(num_samples * 0.1)
    }
    
    # Ajuste por redondeo
    current_total = sum(counts.values())
    if current_total < num_samples:
        counts['O(n)'] += (num_samples - current_total)

    # Generación
    for _ in range(counts['O(1)']):
        dataset.append({"pseudocode": gen_o_1(), "complexity": "O(1)"})
        
    for _ in range(counts['O(log n)']):
        dataset.append({"pseudocode": gen_o_log_n(), "complexity": "O(log n)"})
        
    for _ in range(counts['O(n)']):
        dataset.append({"pseudocode": gen_o_n(), "complexity": "O(n)"})
        
    for _ in range(counts['O(n^2)']):
        dataset.append({"pseudocode": gen_o_n2(), "complexity": "O(n^2)"})
        
    for _ in range(counts['O(n^3)']):
        dataset.append({"pseudocode": gen_o_n3(), "complexity": "O(n^3)"})

    for _ in range(counts['O(2^n)']):
        dataset.append({"pseudocode": gen_o_2n(), "complexity": "O(2^n)"})
        
    # Mezclar para que no queden ordenados
    random.shuffle(dataset)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        
    print(f"✅ ¡Éxito! Se generó '{OUTPUT_FILE}' con {len(dataset)} ejemplos.")

if __name__ == "__main__":
    generate_dataset(NUM_SAMPLES)