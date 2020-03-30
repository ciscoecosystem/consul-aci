var webpack = require('webpack');
var path = require('path');

var BUILD_DIR = path.resolve(__dirname, 'src/client/public');
var APP_DIR = path.resolve(__dirname, 'src/client/app');

var config = {
    entry: APP_DIR + '/login.js',
    node: {
        console: false,
        fs: 'empty',
        net: 'empty',
        tls: 'empty'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?/,
                include: APP_DIR,
                loader: 'babel-loader',
                options: {
                    "presets": [
                        "es2015",
                        "react"
                    ],
                    "plugins": [
                        "transform-object-rest-spread"
                    ]
                }
            },
            {
                test: /\.css$/,
                loaders: ['style-loader', 'css-loader'],
            }
        ]
    },
    output: {
        path: BUILD_DIR,
        filename: 'login.js'
    }
};

module.exports = config;

