const webpack = require('webpack');
const TerserPlugin = require("terser-webpack-plugin");
const path = require('path');
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { VueLoaderPlugin } = require('vue-loader');


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
                // inject: false,
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
        new webpack.ProgressPlugin(),
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
