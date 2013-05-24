'''
Created on Dec 7, 2012

@author: AcidTonic

This is property of Zach Davis aka "AcidTonic". All rights reserved. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Checks for logs to convert one folder ABOVE the location of the script. 
Makes a copy of the .csv file with the name + .converted.csv
Will not delete files or recreate them if they already exist. Delete the .converted.csv file to rebuild it if you changed the original.

If you place this script in a folder on the Tactrix, it will automatically find new logs and parse/convert/alert on them. 
Only new files will be processed and you can watch the console to see which logs match whatever rules you have setup.

Install python 2.x windows binaries to run this program on Windows.

To build an EXE (not required), download pyinstaller and run python -O pyinstaller.py "absolute/path/to/LogFixer.py"

They aren't exactly "compiled" and won't properly hide the source code. 
Skilled people can turn the pyd files inside the exe back into .py source files!

The point of the EXE is to help users avoid setting up python! Not to hide your secrets!

Good luck!

'''

import os
import sys
import datetime


''' Datastructure that represents a loaded Log File.'''
class Log:
    def __init__(self):
        self.headers = []
        self.rows_by_header = {}   
        self.filename = ''
        self.converted_filename = ''

''' Class that reads and parses log files from disk, returning Log instances '''
class LogReader():    
    def parse_log(self,path):
        new_log = Log()
        new_log.filename = path
        
        #Open log
        log_file = file(path)
        
        #Read first line to parse headers
        first_line = log_file.readline()
        if not first_line:
            raise Exception('Problem')
        
        #Split line by comma for headers
        first_line = first_line.strip()
        first_line = first_line.replace('\n', '')
        first_line = first_line.replace('\r', '')
        first_line = first_line.replace('\r\n', '')
            
        new_log.headers = first_line.split(',')
        
        #Create empty lists for each header
        for header in new_log.headers:
            new_log.rows_by_header[header] = []
            
        
        #Read headers until done
        while True:
            line = log_file.readline()
            if not line:
                break
            
            #Split row by same delimiter
            one_row = line.strip()
            one_row = one_row.replace('\n', '')
            one_row = one_row.replace('\r', '')
            one_row = one_row.replace('\r\n', '')
            one_row = one_row.split(',')
            
            #Sanity check that same number of columns were found as headers. 
            #Otherwise something was not escaped (And we don't support escaping currently so don't!)
            if len(one_row) != len(new_log.headers):
                raise Exception('Encountered row with different number of columns than headers')
            
            
            #Read every header, for every row, into a single datastructure.
            for index, header in enumerate(new_log.headers):
                new_log.rows_by_header[header].append(one_row[index])
                
        #Return the crafted Log
        return new_log

class LogWriter():
    def __init__(self):
        pass
    
    def write_log(self, log, filename):
        log_file = file(filename,'w')
        row_length = None
        for header in log.headers:
            if not row_length:
                row_length = len(log.rows_by_header[header])
            if len(log.rows_by_header[header]) != row_length:
                raise Exception('Found uneven rows per header')
        
        
        #Write headers
        for index, header in enumerate(log.headers):
            if index == 0:
                log_file.write('%s' % header)
            else:
                log_file.write(',%s' % header)
        log_file.write('\n')
        
        #Now write rows
        for row_index in range(row_length):
            next_row = ''
            
            for index, header in enumerate(log.headers):
                if index == 0:
                    next_row = next_row + '%s' % log.rows_by_header[header][row_index]
                else:
                    next_row = next_row + ',%s' % log.rows_by_header[header][row_index]
            next_row = next_row + '\n'
            log_file.write(next_row)
        
        log_file.close()
             

''' Class that converts Log datastructures to various formats'''
class LogFixer:
    def __init__(self):
        pass
        # 'LogEntryDate', 'LogEntryTime' and 'LogEntrySeconds'
        #
        # 2012-11-01, 16:35:42.95312, 0.48603
        #
        # 2012-11-01, 16:35:42.95312, 0.74014
        #
    
    def fix_id(self,log):
        new_log = Log()
        new_log.headers = log.headers
        new_log.rows_by_header = log.rows_by_header
        new_log.converted_filename = log.converted_filename
        new_log.filename = log.filename
        
        if 'sample' in new_log.headers:
            
            new_log.rows_by_header['LogID'] = new_log.rows_by_header['sample']
            new_log.headers.append('LogID')
            new_log.headers.remove('sample')
            del new_log.rows_by_header['sample']
        return new_log
    
    def fix_order(self,log):
        headers = log.headers
        new_headers = []
        #LogID,LogEntryDate,LogEntryTime,LogEntrySeconds
        if 'LogID' in headers:
            new_headers.append('LogID')
            headers.remove('LogID')
        if 'LogEntryDate' in headers:
            new_headers.append('LogEntryDate')
            headers.remove('LogEntryDate')
        if 'LogEntryTime' in headers:
            new_headers.append('LogEntryTime')
            headers.remove('LogEntryTime')
        if 'LogEntrySeconds' in headers:
            new_headers.append('LogEntrySeconds')
            headers.remove('LogEntrySeconds')
        for remaining_header in headers:
            new_headers.append(remaining_header)
        return new_headers
        
    def fix_dates(self,log):
        if log.rows_by_header.has_key('LogEntryDate'):
            raise Exception("It appears this log already has valid dates")
        
        now = datetime.datetime.now()
        new_log_date = now.strftime('%Y-%m-%d')
        
        new_log = Log()
        new_log.headers = log.headers
        new_log.rows_by_header = log.rows_by_header
        new_log.converted_filename = log.converted_filename
        new_log.filename = log.filename
        
        length = len(new_log.rows_by_header[new_log.headers[0]])
        new_log.rows_by_header['LogEntryDate'] = []
        for i in range(length):
            new_log.rows_by_header['LogEntryDate'].append('%s' % new_log_date)
        new_log.headers.append('LogEntryDate')
        return new_log
    
    def fix_times(self,log):
        if log.rows_by_header.has_key('LogEntryTime'):
            raise Exception("It appears this log already has valid LogEntryTime")
        
        if not log.rows_by_header.has_key('time'):
            raise Exception("This log has no entry 'time' which we need to properly calculate LogEntryTime!")
        
        
        new_log = Log()
        new_log.headers = log.headers
        new_log.rows_by_header = log.rows_by_header
        new_log.converted_filename = log.converted_filename
        new_log.filename = log.filename
        
        length = len(new_log.rows_by_header[new_log.headers[0]])
        new_log.rows_by_header['LogEntryTime'] = []
        new_log.headers.append('LogEntryTime')
        
        for i in range(length):
            time_string = new_log.rows_by_header['time'][i]
            time_from_string = datetime.timedelta(seconds=float(time_string))
            #16:35:42.95312        
            if i == 0:
                last_time_from_string = time_from_string
                #new_log_time = time_from_string.strftime('%H:%M:%S.%f')
                total_seconds = int(time_from_string.total_seconds())
                hours, remainder = divmod(total_seconds,60*60)
                minutes, seconds = divmod(remainder,60)
                new_log_time = '{0:2g}:{1:2g}:{2:2g}.{3:5g}'.format(hours,minutes,seconds,time_from_string.microseconds)
            else:
                time_delta = time_from_string - last_time_from_string
                #new_log_time = time_delta.strftime('%H:%M:%S.%f')
                total_seconds = int(time_delta.total_seconds())
                hours, remainder = divmod(total_seconds,60*60)
                minutes, seconds = divmod(remainder,60)
                
                #new_log_time = '%02d:%02d:%02d.%05d' % (hours,minutes,seconds,time_delta.microseconds)
                
                new_log_time = '{0:2g}:{1:2g}:{2:2g}.{3:5g}'.format(hours,minutes,seconds,time_delta.microseconds)
                
                #{0:.5g}

            new_log.rows_by_header['LogEntryTime'].append('%s' % new_log_time)
        return new_log
    
    def fix_seconds(self, log):
        if log.rows_by_header.has_key('LogEntrySeconds'):
            raise Exception("It appears this log already has valid LogEntrySeconds")
        
        if not log.rows_by_header.has_key('time'):
            raise Exception("This log has no entry 'time' which we need to properly calculate LogEntrySeconds!")
        
        
        new_log = Log()
        new_log.headers = log.headers
        new_log.rows_by_header = log.rows_by_header
        new_log.converted_filename = log.converted_filename
        new_log.filename = log.filename
        
        new_log.rows_by_header['LogEntrySeconds'] = [] 
        
        for entry in new_log.rows_by_header['time']:
            new_log_seconds = '{0:.5g}'.format(float(entry))
            new_log.rows_by_header['LogEntrySeconds'].append(new_log_seconds)
        new_log.headers.append('LogEntrySeconds')
        
        return new_log
    
class FilterRule():
    def __init__(self):
        self.action = ''
        self.expression = ''
        self.name = ''
        
class LogFilter():
    def __init__(self,alerts_path):
        self.alerts_path = alerts_path
        self.rules = {}
        self.log_writer = LogWriter()
        
    def parse_filters(self,filename):
        config_file = file(filename, 'r')
        
        #RuleName: Knock with Load
        #RuleExpression: KnockSum > 3 and Load > 100
        #RuleAction: move
        
        expecting = 'rulename:'
        new_rule = FilterRule()
        
        #Read until done
        while True:
            line = config_file.readline()
            if not line:
                if expecting != 'rulename:':
                    raise Exception('Error parsing rules.conf! Expected "%s" not EOF' % expecting)
                break
            
            #process line
            line = line.strip()
            line = line.replace('\n', '')
            line = line.replace('\r', '')
            line = line.replace('\r\n', '')
        
            print line
            if line.lower().startswith(expecting):
                        
                if expecting == 'rulename:':
                    new_rule.name = line.split(':')[1].strip()
                    print new_rule.name
                    expecting = 'ruleexpression:'
                    continue
                if expecting == 'ruleexpression:':
                    new_rule.expression = line.split(':')[1].strip()
                    print new_rule.expression
                    expecting = 'ruleaction:'
                    continue
                if expecting == 'ruleaction:':
                    new_rule.action = line.split(':')[1].strip()
                    print new_rule.action
                    expecting = 'rulename:'
                    self.rules[new_rule.name] = new_rule
                    new_rule = FilterRule()
                    continue
            else:
                if not line or len(line) < 0 or line.startswith('#') or line.startswith(';'):
                    continue
                raise Exception('Failed parsing rules.conf, unexpected line "%s"' % line)
                
        print self.rules
        
        
    def apply_filters(self,log):
        for rule_name in self.rules:
            rule = self.rules[rule_name]
            print 'Evaluating rule "%s"' % rule.name
            
            match = False
            
            for index in range(len(log.rows_by_header[log.headers[0]])):
            
                expression = rule.expression
                for header in log.headers:
                    expression = expression.replace(header,log.rows_by_header[header][index])
            
                try:
                    result = eval(expression)
                except:
                    result = False
                if result:
                    match = True
                    break
                #print expression
                #print index
                #print "result of Eval was '%s'" % result
            
            if match:
                
                if rule.action == 'move':
                    print '%s matched rule "%s"' % (log.filename,rule.name)
                    
                    if not os.path.exists(alerts_path):
                        os.mkdir(alerts_path)
                        if not os.path.exists(alerts_path):
                            raise Exception('Unable to create rule output folder "%s"' % alerts_path)
                    
                    
                    new_rule_path = os.path.join(self.alerts_path,rule.name)
                    if not os.path.exists(new_rule_path):
                        os.mkdir(new_rule_path)
                        if not os.path.exists(new_rule_path):
                            raise Exception('Unable to create rule output folder "%s"' % new_rule_path)
                    new_log_path = os.path.join(new_rule_path,log.converted_filename)
                    self.log_writer.write_log(log, new_log_path)
                    continue
                else:
                    raise Exception("Unknown rule action '%s'" % rule.action)
                    
            #KnockSum > 3 and Load > 100
            #log.rows_by_header
            #log.rows_by_header['KnockSum'][index] > 3 and log.rows_by_header['Load'][index] > 100
            
            #5 > 3 and 80 > 100
            #(FALSE)
             
            
            
if __name__ == '__main__':
    
    import sys, os
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    #current_dir = 'C:\Tactrix Simulation'
    current_dir = os.path.join(base_dir,'..')
    config_path = os.path.join(base_dir,'rules.conf')
    alerts_path = os.path.join(current_dir,'Alerts')
    print config_path
    if os.path.exists(config_path):
        log_filter = LogFilter(alerts_path)
        log_filter.parse_filters(config_path)
    log_reader = LogReader()
    log_writer = LogWriter()
    log_fixer = LogFixer()
                            
    
    print 'Looking for *.csv inside "%s"' % current_dir
    
    try:
        os.chdir(current_dir)
    except:
        raise Exception("Fatal: Unable to change directory to '%s'" % current_dir)
    
    current_files = os.listdir(os.curdir)
    
    for filename in current_files:
        
        if filename.lower().endswith('.converted.csv'):
            print 'Skipping the converted file %s' % filename
            continue
        if filename.lower().endswith('.csv'):
            
            new_filename = filename[:-4] + '.converted.csv'
            if new_filename in current_files:
                print 'Skipping file with converted version in this folder %s' % filename
                continue
            
            print 'Converting %s' % filename                        
            
            try:
                log = log_reader.parse_log(filename)
                
                log.converted_filename = new_filename
                
                #Fix log....
                fixed_log = log_fixer.fix_dates(log)
                fixed_log = log_fixer.fix_times(fixed_log)
                fixed_log = log_fixer.fix_seconds(fixed_log)
                fixed_log = log_fixer.fix_id(fixed_log)
                
                
                fixed_log.headers = log_fixer.fix_order(fixed_log)
                
                if log_filter:
                    log_filter.apply_filters(fixed_log)
                
                log_writer.write_log(fixed_log, new_filename)
                
            except Exception as e:
                print e    
                print '%s: %s' % (filename,e.message)
    
