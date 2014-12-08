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
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
        });
        
        grading.transferZoobars("u2", 1, function() {
            //console.log("transfer 1");
            console.log("transfer of 1 zoobar from u1 to u2 is launched 10 times");
            console.log("login to localhost:8080/zoobar/index.cgi/users?user=u1 as u2:u2 to see the zoobars and transfer logs");
            phantom.exit();
        });
    });
}

main.apply(null, system.args.slice(1));
