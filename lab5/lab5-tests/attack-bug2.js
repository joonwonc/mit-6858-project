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
    	grading.transferZoobars("attacker", 10, function() {
    	
    		console.log("Sending 10 zoobars");
    	});
    	
    	// load attacker's account
        phantom.cookies = auth.attackerCookies;
        
        // check cookie number
        grading.getZoobars(function(number) {
        	if (number != 20) {
        		console.log("FAIL - attacker has " + number + " zoobars, should have 20");
        	} else {
        		console.log("PASS - attacker zoobar count");
        	}

        	phantom.exit();
        });
    });    
}

main.apply(null, system.args.slice(1));
