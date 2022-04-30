# Robô da Innovar

## Documentação
### Menus
```js
{
    "options": 
        // Aqui estarão as opções.
        "*": {
            // Aqui estarão as opções para qualquer opção anterior
            "index": {
                "prompt": "texto",
                "action": "menu#nomeDoMenu@Index" 
                /* 
                 * Pimeiro item indica a ação
                 * Segundo dá contexto
                 * Terceiro dá argumentos.
                 * 
                 * no caso de menu#nomeDoMenu@Index
                 * a ação é menu, o contexto nomeDoMenu e o argumento é Index
                 * Ou seja, chamará o menu nomeDoMenu e dará as opções para Index.
                 */
            }
        }

}
```