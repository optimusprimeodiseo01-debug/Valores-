# THREAT MODEL - KEY LEAKS

## Vectores principales

A) Repositorio

key.txt → git add → commit → push
→ fuga total

---

B) Codigo

private_key = "0x..."

→ queda en historial git

---

C) Logs

print(tx)
print(account)

→ posible exposicion indirecta

---

D) Runtime

robot + signer juntos

→ acceso compartido

---

E) Red local

socket sin control

→ firma de tx externas

---

F) Permisos

key.txt sin chmod 600

→ lectura por otros usuarios

---

## Condicion critica

SI ocurre cualquiera:

→ perdida irreversible de control
