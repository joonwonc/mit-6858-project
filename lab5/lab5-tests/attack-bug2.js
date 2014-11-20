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
                console.log("1 attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("2 attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("3 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("4 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("5 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("6 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("7 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("8 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("9 attacker", 1, function() {
            phantom.cookies = auth.attackerCookies;
            grading.getZoobars(function(number2) {
                console.log("attacker has: " + number2);
                phantom.exit();
            });
        });
        
        grading.transferZoobars("10 attacker", 1, function() {
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
