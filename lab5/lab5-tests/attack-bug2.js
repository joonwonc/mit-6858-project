var fs = require("fs");
var system = require("system");
var webpage = require("webpage");

var grading = require("./grading");

function main(studentDir) {
    if (studentDir === undefined) {
        console.log("USAGE: phantomjs " + system.args[0] + " student_dir/");
        phantom.exit();
        return;
    }
    
    grading.registerTimeout(60);

    // First login.
    grading.initUsers(function(auth) {
        
        // print log statements
        console.log("Create accounts");
        // load grader's cookies
        phantom.cookies = auth.graderCookies;
        // transfer zoobars to the attacker
        
        // begin 10
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        // end of 10
    });
}

main.apply(null, system.args.slice(1));
