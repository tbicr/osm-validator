var path = require('path')

module.exports = {
    entry: "./osm_validator_front/js/index.jsx",
    output: {
        path: __dirname,
        filename: "./static/js/app_bundle.js"
    },
    module: {
        rules: [
            {
                test: /\.js?$/,
                enforce: "pre",
                loaders: ['eslint'],
                include: [
                    path.resolve(__dirname,	"osm_validator_front/js"),
                ],
            }, {
                test: /\.css$/,
                loader: "style-loader!css-loader"
            }, {
                test: /\.jsx$/,
                exclude: /node_modules/,
                loader: ["babel-loader", "eslint-loader"]
            }
        ]
    }
};