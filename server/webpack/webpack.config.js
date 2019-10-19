const path = require('path');
const { VueLoaderPlugin } = require('vue-loader');
const HtmlWebpackPlugin = require("html-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = {
    mode: 'production',
    entry: './src/index.js',
    output: {
        filename: 'main.[contentHash].js',
        path: path.resolve(__dirname, '../app/static/generated'),
    },
    optimization: {
        minimizer: [
            new TerserPlugin(),
            new HtmlWebpackPlugin({
                inject: false,
                filename: "../../templates/base_generated.html",
                template: "./src/base_template.html",
                minify: {
                    removeAttributeQuotes: true,
                    collapseWhitespace: true,
                    removeComments: true
                }
            })
        ],
        splitChunks: {
            chunks: 'all'
        }
    },
    plugins: [
        new VueLoaderPlugin()
    ],
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            }
        ]
    },
};
