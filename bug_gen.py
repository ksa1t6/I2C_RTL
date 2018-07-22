import subprocess
import sys
import random
#arg1 is opencore design directory


#git steps
#git init
#git add .
#git commit -m "First Commit"
#git remote add origin https://github.com/sudumon/fpu.git
#git remote -v
#git push origin master


#Pre-processing
#1. Get list of golden rtl files into array
#2. Create copy of golden file in test directory
#3. Create 2-D array for potential buggy lines(Order by 1st level by file names in file name array, 2nd level is assign or register assignment statement)
#4. Create 2-D array for buggy line history (Order 1st level by file names in file name array, 2nd level is string pair (correctline;buggyline), remove ; at end of lines and put them back


design = sys.argv[1]
#print 'DESIGN: ', design


file_list_string = subprocess.check_output(['ls', 'original'])
file_list = file_list_string.split('\n')
file_list.pop()

assign_bug_list = []
register_bug_list = []

#print 'FILE LIST:'
for i in xrange(0,len(file_list)):
    #print file_list[i]
    grep_target = 'original/' + file_list[i]
    grep1 = subprocess.Popen( ['grep', ';', grep_target], stdout=subprocess.PIPE)
    grep2 = subprocess.Popen( ['grep', 'assign'], stdin=grep1.stdout, stdout=subprocess.PIPE)
    assign_bugs = grep2.communicate()[0].split('\n')
    assign_bugs.pop()
    #print assign_bugs
    
    grep1 = subprocess.Popen( ['grep', '-v', 'for', grep_target], stdout=subprocess.PIPE)
    grep2 = subprocess.Popen( ['grep', '<='], stdin=grep1.stdout, stdout=subprocess.PIPE)
    register_bugs = grep2.communicate()[0].split('\n')
    register_bugs.pop()
    #print register_bugs

    file_bug_pair = (file_list[i], assign_bugs)
    assign_bug_list.append( file_bug_pair )
    
    file_bug_pair = (file_list[i], register_bugs)
    register_bug_list.append( file_bug_pair )


assign_bug_dict = dict(assign_bug_list)
register_bug_dict = dict(register_bug_list)

for i in xrange(0,len(file_list)):
    #print "FILE: " + file_list[i]
    cur_bug_list = assign_bug_dict.get(file_list[i])
    #for j in xrange(0,len(cur_bug_list)):
        #print cur_bug_list[j]
    cur_bug_list = register_bug_dict.get(file_list[i])
    #for j in xrange(0,len(cur_bug_list)):
    #    print cur_bug_list[j]


'''
Have dictionary (bug, in use) so we do not repeat bugs
Have dictionary (buggy line, good line) so we can fix bugs easily

Randomness

1) Pick file at random to operate on 
2) Pick either (insert bug or dummy edit if no bugs, if all bugs used then revert or dummy edit)
    a) Insert bug
        i) Assign bug
        ii) Register delay bug
        iii) After picking bug substitute line
    b) Revert bug
        i) Search dictionary (buggy, correct) pairs to see if bug exists and then fix
        ii) Substitute line to fix bug
    c) Dummy edit
        i) Add comment to end of file
3) Edit file
'''

op = random.randint(0,2)
file_index = random.randint(0, len(file_list) - 1)
assign_bug_index = random.randint(0, len( assign_bug_dict.get( file_list[file_index]) ) -1 )
register_bug_index = random.randint(0, len( register_bug_dict.get( file_list[file_index]) ) -1 )

#print assign_bug_index
#print register_bug_index

bug_type = random.randint(0,2)

candidate_line = "CANDIDATE"
buggy_line = "BUGGY"

# ASSIGN BUG
if bug_type == 0 or bug_type == 1:
    if bug_type == 0:
        candidate_line = assign_bug_dict.get(file_list[file_index])[assign_bug_index]
    elif bug_type == 1:
        candidate_line = register_bug_dict.get(file_list[file_index])[register_bug_index]

    assign_bug_value = random.randint(0,1)

    if assign_bug_value == 0:
        buggy_line = candidate_line.split('=')[0] + '= 1;'
    elif assign_bug_value == 1:
        buggy_line = candidate_line.split('=')[0] + '= 0;'
elif bug_type == 2:
    candidate_line = register_bug_dict.get(file_list[file_index])[register_bug_index]
    buggy_line = candidate_line
    
    while candidate_line == buggy_line:
        temp_line = candidate_line.split()
        temp_line[2] = "#" + str( random.randint(1,9) )
        buggy_line = " ".join(temp_line)

temp = candidate_line.split('/')
candidate_line = temp[0].strip()

back_comma_index = candidate_line.find('`')

if back_comma_index != -1:
    candidate_line = candidate_line[:back_comma_index] + "\\" + candidate_line[back_comma_index:]

temp = buggy_line.split('/')
buggy_line = temp[0].strip()

back_comma_index = buggy_line.find('`')

if back_comma_index != -1:
    buggy_line = buggy_line[:back_comma_index] + "\\" + buggy_line[back_comma_index:]

print candidate_line + "\nis going to be replaced by\n" + buggy_line + "\nin file " + file_list[file_index]

#out_file = open("buggy/"+file_list[file_index], "w")
print 'sed ' + '-i ' +"\"s/"+candidate_line+"/"+buggy_line+"/g\" " +"original/"+file_list[file_index]
subprocess.call([ 'sed ' + '-i ' +"\"s/"+candidate_line+"/"+buggy_line+"/g\" " +"buggy/"+file_list[file_index] ], shell=True)
