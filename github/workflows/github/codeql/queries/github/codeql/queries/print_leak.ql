/**
 * Detecta prints potencialmente peligrosos
 */

import python

from CallExpr call
where
  call.getFunc().getName() = "print" and
  exists(Expr arg |
    arg = call.getAnArgument() and
    arg.toString().regexpMatch("key|private|account|secret")
  )
select call, "Posible fuga por print de informacion sensible."
