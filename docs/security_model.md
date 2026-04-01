# SECURITY MODEL - VALORES-

## Superficie del sistema

                SISTEMA VALORES-

        [ ROBOT CLIENT ]
                |
                | tx (sin firmar)
                v
        [ SIGNER (clave privada) ]
                |
                | tx firmada
                v
            BLOCKCHAIN (Ω)

## Punto critico

PRIVATE_KEY → infra/key.txt

La clave define control total del sistema.

## Regla base

la clave no debe salir del signer
