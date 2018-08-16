'use strict'
const path = require('path')
const utils = require('./utils')
const webpack = require('webpack')
const config = require('../config')
const merge = require('webpack-merge')
const baseWebpackConfig = require('./webpack.base.conf')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const OptimizeCSSPlugin = require('optimize-css-assets-webpack-plugin')
const SWPrecacheWebpackPlugin = require('sw-precache-webpack-plugin')
const loadMinified = require('./load-minified')
const WorkboxPlugin = require('workbox-webpack-plugin')

const env = process.env.NODE_ENV === 'testing'
  ? require('../config/test.env')
  : config.build.env

const webpackConfig = merge(baseWebpackConfig, {
  module: {
    rules: utils.styleLoaders({
      sourceMap: config.build.productionSourceMap,
      extract: true
    })
  },
  devtool: config.build.productionSourceMap ? '#source-map' : false,
  output: {
    path: config.build.assetsRoot,
    filename: utils.assetsPath('js/[name].[chunkhash].js'),
    chunkFilename: utils.assetsPath('js/[id].[chunkhash].js')
  },
  plugins: [
    // http://vuejs.github.io/vue-loader/en/workflow/production.html
    new webpack.DefinePlugin({
      'process.env': env
    }),
    // UglifyJs do not support ES6+, you can also use babel-minify for better treeshaking: https://github.com/babel/minify
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false
      },
      sourceMap: true
    }),
    // extract css into its own file
    new ExtractTextPlugin({
      filename: utils.assetsPath('css/[name].[contenthash].css')
    }),
    // Compress extracted CSS. We are using this plugin so that possible
    // duplicated CSS from different components can be deduped.
    new OptimizeCSSPlugin({
      cssProcessorOptions: {
        safe: true
      }
    }),
    // generate dist index.html with correct asset hash for caching.
    // you can customize output by editing /index.html
    // see https://github.com/ampedandwired/html-webpack-plugin
    new HtmlWebpackPlugin({
      filename: process.env.NODE_ENV === 'testing'
        ? 'index.html'
        : config.build.index,
      template: 'webpack-template.html',
      inject: false,
      minify: {
        removeComments: true,
      },
      // necessary to consistently work with multiple chunks via CommonsChunkPlugin
      chunksSortMode: 'dependency',
      serviceWorkerLoader: `<script>${loadMinified(path.join(__dirname,
        './service-worker-prod.js'))}</script>`
    }),
    // keep module.id stable when vender modules does not change
    new webpack.HashedModuleIdsPlugin(),
    // split vendor js into its own file
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      minChunks: function (module) {
        // any required modules inside node_modules are extracted to vendor
        return (
          module.resource &&
          /\.js$/.test(module.resource) &&
          module.resource.indexOf(
            path.join(__dirname, '../node_modules')
          ) === 0
        )
      }
    }),
    // extract webpack runtime and module manifest to its own file in order to
    // prevent vendor hash from being updated whenever app bundle is updated
    new webpack.optimize.CommonsChunkPlugin({
      name: 'manifest',
      chunks: ['vendor']
    }),
    // service worker caching
    new SWPrecacheWebpackPlugin({
      cacheId: 'hgtv',
      filename: 'service-worker.js',
      filepath: path.resolve(__dirname, '../../static/service-worker.js'),
      minify: false,
      dontCacheBustUrlsMatching: /./,
      directoryIndex: '/',
      staticFileGlobs: ['../static/build/**/*.{js,css}', '../static/img/*.{ico,png}', '../static/thumbnails/*.{png,jpg,jpeg'],
      stripPrefixMulti: {
        '../static/': '/static/'
      },
      runtimeCaching: [{
        urlPattern: '/^https?\:\/\/static.*/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'assets'
          },
        },
      },
      {
        // For development setup
        urlPattern: '/^http:\/\/localhost:5000\/static/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'assets'
          },
        },
      },
      {
        urlPattern: '/^https?\:\/\/ajax.googleapis.com\/*/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'cdn-libraries'
          },
        },
      },
      {
        urlPattern: '/^https?:\/\/cdnjs.cloudflare.com\/*/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'cdn-libraries'
          },
        },
      },
      {
        urlPattern: '/^https?:\/\/images\.hasgeek\.com\/embed\/file\/*/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'images'
          },
        },
      },
      {
        urlPattern: '/^https?:\/\/imgee\.s3\.amazonaws.com\/imgee\/*/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'images'
          },
        },
      },
      {
        urlPattern: '/^https?:\/\/fonts.gstatic.com\/*/',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'fonts'
          },
        },
      },
      {
        urlPattern: '/(.*)',
        handler: 'networkFirst',
        options: {
          cache: {
            name: 'routes'
          },
        },
      }
      ]
    })
  ]
})

if (config.build.productionGzip) {
  const CompressionWebpackPlugin = require('compression-webpack-plugin')

  webpackConfig.plugins.push(
    new CompressionWebpackPlugin({
      asset: '[path].gz[query]',
      algorithm: 'gzip',
      test: new RegExp(
        '\\.(' +
        config.build.productionGzipExtensions.join('|') +
        ')$'
      ),
      threshold: 10240,
      minRatio: 0.8
    })
  )
}

if (config.build.bundleAnalyzerReport) {
  const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
  webpackConfig.plugins.push(new BundleAnalyzerPlugin())
}

module.exports = webpackConfig
