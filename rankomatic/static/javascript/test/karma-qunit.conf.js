// Karma configuration
// Generated on Thu Feb 19 2015 16:00:50 GMT-0700 (MST)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '..',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['qunit', 'jasmine'],


    // list of files / patterns to load in the browser
    files: [
      // dependencies
      {pattern: 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
       watched: false, served: true, included: true},
      {pattern: '../scripts/handlebars-v2.0.0.js', watched: false, served: true, included: true},
      'node_modules/jasmine-jquery/lib/jasmine-jquery.js',

      // fixtures
      {pattern: 'test/qunit/test.html', watched: true, included: true, served: true},
      {pattern: 'test/qunit/tools.js', watched: true, served: true, included: true},
      {pattern: 'test/qunit/test*.js', watched: true, served: true, included: true},

      // source
      {pattern: '*.js', watched: true, served: true, included: true},

    ],

    // list of files to exclude
    exclude: [
      "account.js", "example_edit.js", "grammars.js", "tableaux.js", "entailments.js"
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9877,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Chrome', 'Firefox'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true
  });
};
