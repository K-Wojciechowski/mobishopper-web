module.exports = {
    root: true,
    env: {
        node: true,
    },
    extends: [
        "plugin:vue/essential",
        "@vue/airbnb",
        "@vue/typescript/recommended",
    ],
    parserOptions: {
        ecmaVersion: 2020,
    },
    globals: {
        gettext: false
    },
    rules: {
        "no-undef": [0],  // does not understand ts types
        "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
        "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
        "class-methods-use-this": [0],
        "max-classes-per-file": [0],
        "object-curly-spacing": [2, "never"],
        quotes: [1, "double"],
        indent: [0, 4],
        "max-len": [1, 120],
        "vue/script-indent": [0, 4, { baseIndent: 1 }],
        "vue/html-indent": [0, 4, { baseIndent: 1 }],
        "lines-between-class-members": [0],
        "@typescript-eslint/camelcase": [0],
        "@typescript-eslint/ban-ts-ignore": [0],  // just plain stupid
        "@typescript-eslint/no-inferrable-types": [0],
        "no-param-reassign": [2, {"props": false}],
    },
};
