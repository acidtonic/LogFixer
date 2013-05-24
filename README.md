LogFixer
========

Converts Tactrix logfiles to Evoscan format along with other scanning features


* LogFixer Documentation
* Version 1.0 By: Zach Davis All Rights Reserved.
* License: __GPL__

#Description

This program converts standalone logs to an Evoscan compatible format.
When ran it searches for logs to convert one folder above the current folder.
This way it can easily be placed neatly in a folder on the root of the Tactrix
and it will automatically find any logfiles that it hasn't already converted.

All discovered log files will be converted only once. They are not deleted.
Instead, copies with the same name but a different extension are created.
This way you can easily sort-by file extension or copy only the converted files.

If a converted version of the log is missing, it will be regenerated.
This means you can directly edit the converted versions of the logs and regenerate
them by simply deleting them and running LogFixer again.

#Configuration

For normal use, nothing is required other than moving the folder to the tactrix flash
device and running LogFixer to convert any new log files.....
but if you want to search the logs for interesting data read on....

#Filtering

All scanned log files are searched for potential matches to *very* basic eval tests...
Upon match the log file will be written to a folder called "Alerts" in a folder with
the same name as the rule. Basically the logs will be copied to each folder that matches
So you can browse into Alerts/Rule Folder to see what logs matched that rule.
It also means the rule name has to be a valid folder name or the tool can't create the folder...

Once setup, I can drive for many hours logging every second and then go home and instantly spot the
bad events (if any) out of many log files... Even if some logs completely lack the exact field I'm testing for...
such as Load or Load1B or whatever. Just make rules for both spellings and if either matches it will work as expected.
Even if I've turned the car on and off 50 times over vacation driving, I can spot the one log file with a 6 count easily
and the 4 other logs out of 50 with questionable events.
Make as many rules as you like... you can have more than two. The format isn't terribly confusing or complex....


      RuleName: Some New Rule You Create
      RuleExpression: LOGFIELD OPERATOR
      RuleAction: ACTION
      
That's it. All 3 rows must exist in that order and can repeat as many times as you like.
>
    LOGFIELD is your log header like Load or Load1B or RPM
    OPERATOR is > < >= <= &%
    ACTION is move (only supported action currently but that may change)
    Lines starting with # or ; are ignored as comments.
    Missing the LOGFIELD are simply considered a non matching rule, nothing else is aborted.
    The RuleName must be first, then RuleExpression, then RuleAction. Each on a separate line. Otherwise parse error


    #sample rules.conf
    RuleName: Knock with Load
    RuleExpression: KnockSum > 3 and Load > 100
    RuleAction: move
    
    RuleName: Knock At all
    RuleExpression: KnockSum > 1 and Load > 20
    RuleAction: move
    
