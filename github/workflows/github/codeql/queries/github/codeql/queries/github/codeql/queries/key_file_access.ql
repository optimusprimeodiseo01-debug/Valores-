/**
 * Detecta acceso a archivos de clave
 */

import python

from CallExpr call
where
  call.getFunc().getName() = "open" and
  exists(Expr arg |
    arg = call.getArgument(0) and
    arg.toString().regexpMatch("key.txt")
  )
select call, "Acceso a archivo de clave detectado. Verificar seguridad."
