# execute the following before running this script:
# export PYTHONIOENCODING=utf-8

# Usage:
# python3 anno.py 711_allan_quatermain_brat.txt 711_allan_quatermain_brat.ann 711_allan_quatermain_brat.out

import sys, re, operator
from collections import Counter

PINK = '\033[95m'
ENDC = '\033[0m'
# Bold High Intensty
BIBlack="\033[1;90m"      # Black
BIRed="\033[1;91m"        # Red
BIGreen="\033[1;92m"      # Green
BIYellow="\033[1;93m"     # Yellow
BIBlue="\033[1;94m"       # Blue
BIPurple="\033[1;95m"     # Purple
BICyan="\033[1;96m"       # Cyan
BIWhite="\033[1;97m"      # White

Black        = "\033[30m"
Red          = "\033[31m"
Green        = "\033[32m"
Yellow       = "\033[33m"
Blue         = "\033[34m"
Magenta      = "\033[35m"
Cyan         = "\033[36m"
LightGray    = "\033[37m"
DarkGray     = "\033[90m"
LightRed     = "\033[91m"
LightGreen   = "\033[92m"
LightYellow  = "\033[93m"
LightBlue    = "\033[94m"
LightMagenta = "\033[95m"
LightCyan    = "\033[96m"
White        = "\033[97m"

On_IBlack="\033[0;100m"   # Black
On_IRed="\033[0;101m"     # Red
On_IGreen="\033[0;102m"   # Green
On_IYellow="\033[0;103m"  # Yellow
On_IBlue="\033[0;104m"    # Blue
On_IPurple="\033[10;95m"  # Purple
On_ICyan="\033[0;106m"    # Cyan
On_IWhite="\033[0;107m"   # White

spans={}
ent_colors={}
color_n=-1
cols=[BIRed, BIGreen, BIBlue, BICyan, LightRed, LightGreen, LightBlue, BIGreen, BIBlue, BICyan, BIYellow, DarkGray]

deps={}


window=500
entities={}
eid=2

names={}
entities={}
counts=Counter()
chunk_id=0

chunk_size=30

curid=0
chunk_id=0

def next_color():
	global color_n
	color_n+=1
	if color_n >= len(cols):
		return ENDC
	return cols[color_n]

def read_text(filename):
	with open(filename, encoding="utf-8") as file:
		return file.read()

female_words={"she":1, "her":1, "herself":1,}
male_words={"he":1, "him":1, "his":1, "himself":1, "her father":1, "her uncle":1}

FEMALE=1
MALE=2

def get_new_mention(pattern, startid, endid, anns, text, index):
	max_id=0
	startbyte=-1
	endbyte=-1
	for (start, end, cat, idd, t) in anns:
		num_id=int(re.sub("T", "", idd))
		if num_id > max_id:
			max_id=num_id
		if idd == startid:
			startbyte=start
		if idd == endid:
			endbyte=end

	p=re.compile(r"\s%s\s" % pattern)

	candidates=[]
	for m in p.finditer(text):
		if m.start() > startbyte and m.end() < endbyte:
			candidates.append(m)

	if len(candidates) == 1:
		return candidates[0], max_id+1
	else:
		if len(candidates) >= index:
			return candidates[index-1], max_id+1
		else:
			print("%s matches for %s between %s and %s" % (len(candidates), pattern, startid, endid))
			if len(candidates) > 0:
				print("Select a number in between %s-%s" % (1, len(candidates)))

	return None, None

def gender(text):
	if text.lower() in female_words:
		return FEMALE
	if text.lower() in male_words:
		return MALE
	return 0

def predict(tid):
	span=spans[tid]
	pred_counts=Counter()

	gen=gender(span)
	all_counts=Counter()

	for eid in entities:
		tt=entities[eid]
		espan=spans[eid]

		e_gen=gender(espan)

		if span.lower() == espan.lower():
			pred_counts[tt]+=1

		if gen != 0:
			if gen != e_gen:
				continue
		
		all_counts[tt]+=1

	if len(pred_counts) > 0:
		k,v=pred_counts.most_common()[0]
		if v > 1:
			return k

	if len(all_counts) > 0:
		k,_=all_counts.most_common()[0]
		return k
	if len(counts) > 0:
		k,_=counts.most_common()[0]
		return k
	return None

def proc_anno(filename):
	anns=[]
	with open(filename, encoding="utf-8") as file:
		for line in file:
			cols=line.rstrip().split("\t")
			idd=cols[0]
			dat=cols[1].split(" ")
			t=cols[2]

			cat=dat[0]
			start=int(dat[1])
			end=int(dat[2])
			if cat.startswith("BEGIN"):
				continue
			# if cat != "PER" and cat != "PRON":
				# continue
			anns.append((start, end, cat, idd, t))
			spans[idd]=t
	return sorted(anns, key = lambda tup: tup[0])

def read_coref(filename):
	global curid
	try:
		with open(filename, encoding="utf-8") as file:
			for line in file:
				cols=line.rstrip().split("\t")
				if cols[0] == "REL":
					source=cols[1]
					target=cols[2]
					label=cols[3]
					deps[source]=(target, label)

				else:
					source=cols[0]
					eid=int(cols[1])
					name=cols[2]
					entities[source]=eid
					names[eid]=name
					counts[eid]+=1
					if eid >= curid:
						curid=eid+1
	except:
		pass


annotationFile=sys.argv[2]
text=read_text(sys.argv[1])
anns=proc_anno(annotationFile)
outFile=sys.argv[3]

read_coref(outFile)


def print_screen():
	global chunk_id, ent_colors
	print ("".join(["="]*120))
	charlen=0
	startchunkpos=0
	line_start_char=0

	words=re.split("\s", text)
	wordanns=[]

	output=[]

	lines=[]
	# 20 words per line
	for i in range(0,len(words), 20):
		lines.append(words[i:i+20])
	chunks=[]

	# 8 lines per chunk
	LINES_PER_CHUNK=12
	for i in range(0, len(lines), LINES_PER_CHUNK):
		chunks.append(lines[i:i+LINES_PER_CHUNK])

	# print (chunks)
	print ("chunk %s of %s" % (chunk_id, len(chunks)))
	if chunk_id < 0:
		chunk_id=0
	if chunk_id >= len(chunks):
		chunk_id=len(chunks)-1

	# for each line (group of 20 words)
	chunk=chunks[chunk_id]

	# print (chunk)

	cur=0
	for i in range(chunk_id):
		ch=chunks[i]
		for line in ch:
			for word in line:
				cur+=len(word)+1

	annotatable={}

	for line in chunk:
		for j,word in enumerate(line):
			wordstart=cur
			wordend=cur+len(word)
			for (start, end, cat, idd, t) in anns:
				if wordstart >=start and wordend <= end:
					annotatable[idd]=start
			cur+=len(word)+1

	sorted_x = sorted(annotatable.items(), key=operator.itemgetter(1))
	target=None
	for k,v in sorted_x:
		if k not in entities and k not in deps:
			target=k
			break
	print ("Target:", target)


	cur=0
	for i in range(chunk_id):
		c=chunks[i]
		for line in c:
			for word in line:
				cur+=len(word)+1


	for line in chunk:
		# print(line)
		maxlen=0
		wordanns=[]
		for j,word in enumerate(line):
			wordann=[]
			wordstart=cur
			wordend=cur+len(word)
			for (start, end, cat, idd, t) in anns:
				if wordstart >=start and wordend <= end:
					wordann.append(idd)
			wordanns.append(wordann)
			# print (wordanns)
			if len(wordann) > maxlen:
				maxlen=len(wordann)
			cur+=len(word)+1


		sentanns=[]
		for j in range(maxlen):
			sentanns.append([])

		lastWord=[None]*maxlen

		# for each word in line
		for j, word in enumerate(line):
		# for j in range(i,i+20):
			# if j < len(words):
			maxwordlen=len(word)
			for k in range(maxlen):
				if len(wordanns[j]) > 0 and len(wordanns[j]) > k and len(wordanns[j][k]) > 0:
					if len(wordanns[j][k]) > maxwordlen:
						maxwordlen=len(wordanns[j][k])
						# print (words[j], maxwordlen, wordanns[j][k], len(words[j]))

			# for each level annotation for that word
			for k in range(maxlen):
				color=ENDC
				if len(wordanns[j]) > 0 and len(wordanns[j]) > k and len(wordanns[j][k]) > 0:
					if wordanns[j][k] != lastWord[k]:
						form=wordanns[j][k] + "".join(["-"]*maxwordlen)
					else:
						form="".join(["-"]*maxwordlen)

					lastWord[k]=wordanns[j][k]
					color=PINK
					if wordanns[j][k] == target:
						color=On_IYellow
					if wordanns[j][k] in entities:
						tmp=entities[wordanns[j][k]]
						# print (tmp, tmp in ent_colors)
						if tmp in ent_colors:
							color=ent_colors[tmp]
						else:
							color=ENDC
					if wordanns[j][k] in deps:
						color=ENDC
				else:
					form="".join([" "]*maxwordlen)
					lastWord[k]=None

				form=color+form[:maxwordlen]+ENDC
				sentanns[k].append(form)


			line[j]=line[j] + "".join([" "]*maxwordlen)
			line[j]=line[j][:maxwordlen]

		for sentann in sentanns:
			output.append (' '.join(sentann))
		output.append (' '.join(line))
		output.append("")


	ents=[]
	for name, v in counts.most_common():
		color=ENDC
		if name in ent_colors:
			color=ent_colors[name]
		entstr="%s\t%s (%d)" % (name, names[name], v)
		lenn=len(entstr[:25])
		entstr=color+entstr[:25]+ENDC+"".join([" "]*(25-lenn))
		ents.append(entstr)


	for i in range(len(output)):
		# outl=len(output[i])
		n=""
		if i < len(ents):
			n=ents[i]
		print ("%s\t%s\t%s" % (n.ljust(25), "|" , output[i].ljust(125)))
	return target

def print_help():	
	print ("".join(["="]*120))	
	print ("Usage:\n")
	print ("n -- creates new entity" )
	print ("n 17 -- creates new entity for mention 17" )
	print ("<enter> -- Accept the suggestion above the prompt (e.g., 'T52 0' links mention T52 to entity 0")
	print ("17 -- links highlighted mention to existing entity 17")
	print ("14 17 -- links mention T14 to existing entity 17")
	print ("-1 -- skip the current mention and go on to the next")
	print ("appos 14 18 -- links mention T14 to mention T18 with apposition relation")
	print ("cop 14 18 -- links mention T14 to mention T18 with copula relation")
	print ("del 14 -- deletes annotation for mention T14")
	print ("entities -- displays all current entities")
	print ("names -- displays all mentions for each entity")
	print ("w -- save annotations to output file")
	print ("q -- quit and save annotations to output file")
	print ("> -- advance to next page")
	print ("< -- go to previous page")
	print ("name 17 the main narrator -- assigns the name 'the main narrator' to entity 17")
	print ("add he 59 0 -- creates a new mention for the first mention of the word 'he' between mention T59 and T0; use this if you see a pronoun that should be linked in coreference but isn't a linkable candidate mention.")
	print ("add he 59 0 2 -- creates a new mention for the second mention of the word 'he' between mention T59 and T0; use this if you see a pronoun that should be linked in coreference but isn't a linkable candidate mention.")
	print ("".join(["="]*120))
	print ("")

print_help()
	
target=print_screen()


lastCommand=""

while(1):
	
	inline=sys.stdin.readline().rstrip()
	if len(inline) == 0:
		inline=lastCommand.split(" # ")[0]
		print ("ZERO")
	print ("#%s#" % inline)

	matcher=re.match("^add (.+) T?(\d+) T?(\d+)$", inline)
	if matcher != None:
		mentionMatch, next_id=get_new_mention(matcher.group(1), "T%s" % matcher.group(2), "T%s" % matcher.group(3), anns, text, 1)
		if mentionMatch is not None:
			start=mentionMatch.start()
			end=mentionMatch.end()
			match_text=mentionMatch.group().lstrip().rstrip()
			print(start, end, match_text, next_id)
			cat="ADDED"
			idd="T%s" % next_id
			anns.append((start, end, cat, idd, match_text))
			spans[idd]=match_text
			out=open(annotationFile, "a")
			out.write("%s\t%s %s %s\t%s\n" % (idd, cat, start, end, match_text))
			out.close()
	matcher=re.match("^add (.+) T?(\d+) T?(\d+) (\d+)?$", inline)
	if matcher != None:
		index=int(matcher.group(4))
		try:
			mentionMatch, next_id=get_new_mention(matcher.group(1), "T%s" % matcher.group(2), "T%s" % matcher.group(3), anns, text, index)
			if mentionMatch is not None:
				start=mentionMatch.start()
				end=mentionMatch.end()
				match_text=mentionMatch.group().lstrip().rstrip()
				print(start, end, match_text, next_id)
				cat="ADDED"
				idd="T%s" % next_id
				anns.append((start, end, cat, idd, match_text))
				spans[idd]=match_text
				out=open(annotationFile, "a")
				out.write("%s\t%s %s %s\t%s\n" % (idd, cat, start, end, match_text))
				out.close()
		except:
			pass

	matcher=re.match("^q$", inline)
	if matcher != None:
		out=open(outFile, "w", encoding="utf-8")
		for tid in entities:
			out.write ("%s\t%s\t%s\n" % (tid, entities[tid], names[entities[tid]]))
		for source in deps:
			(target, cat)=deps[source]
			out.write ("REL\t%s\t%s\t%s\n" % (source, target, cat))

		out.close()
		sys.exit(1)

	matcher=re.match("^appos T?(\d+) T?(\d+)$", inline)
	if matcher != None:
		source="T%s" % matcher.group(1)
		target="T%s" % matcher.group(2)
		if source in entities:
			del entities[source]
		deps[source]=(target, "appos")

	matcher=re.match("^help", inline)
	if matcher != None:
		print_help()

	matcher=re.match("^-1$", inline)
	if matcher != None:
		tid=target
		tid=re.sub("T", "", tid)
		entities["T%s" % tid] = -1
		names[-1]="NONE"

	matcher=re.match("^del T?(\d+)$", inline)
	if matcher != None:
		idd="T%s" % matcher.group(1)
		del entities[idd]

	matcher=re.match("^cop T?(\d+) T?(\d+)$", inline)
	if matcher != None:
		source="T%s" % matcher.group(1)
		target="T%s" % matcher.group(2)
		print (entities)
		if source in entities:
			print ("del source", source)
			del entities[source]
		deps[source]=(target, "cop")


	matcher=re.match("^w$", inline)
	if matcher != None:
		out=open(outFile, "w", encoding="utf-8")
		for tid in entities:
			out.write ("%s\t%s\t%s\n" % (tid, entities[tid], names[entities[tid]]))
		for source in deps:
			(target, cat)=deps[source]
			out.write ("REL\t%s\t%s\t%s\n" % (source, target, cat))

		out.close()

	matcher=re.match("^entities$", inline)
	if matcher != None:
		for tid in entities:
			print ("ENTITY: %s\t%s" % (tid, entities[tid]))
	
	matcher=re.match("^names$", inline)
	if matcher != None:
		t_names={}
		for tid in entities:
			eid=entities[tid]
			if eid not in t_names:
				t_names[eid]=Counter()
			t_names[eid][spans[tid].lower()]+=1

		for eid, v in counts.most_common():
			vals=[]
			for k,c in t_names[eid].most_common():
				vals.append("%s:%s" % (k,c))
			print ("VAL: %s\t%s" % (eid, ', '.join(vals)))


	matcher=re.match("^n$", inline)
	if matcher != None:
		tid=target
		tid=re.sub("T", "", tid)
		entities["T%s" % tid]=curid
		counts[curid]+=1
		curid+=1
		names[entities["T%s" % tid]]=spans["T%s" % tid]

	matcher=re.match("^(\d+)$", inline)
	if matcher != None:
		tid=target
		tid=re.sub("T", "", tid)
		eid=int(matcher.group(1))
		counts[eid]+=1
		entities["T%s" % tid] = eid
		if eid not in ent_colors:
			ent_colors[eid]=next_color()

	matcher=re.match("T?(\d+) n", inline)
	if matcher != None:
		tid=int(matcher.group(1))
		entities["T%s" % tid]=curid
		counts[curid]+=1
		curid+=1
		names[entities["T%s" % tid]]=spans["T%s" % tid]


	matcher=re.match("T?(\d+) (\d+)", inline)
	if matcher != None:
		tid=int(matcher.group(1))
		eid=int(matcher.group(2))
		counts[eid]+=1
		entities["T%s" % tid] = eid
		if eid not in ent_colors:
			ent_colors[eid]=next_color()

	matcher=re.match("name (\d+) (.+)$", inline)
	if matcher != None:
		nid=int(matcher.group(1))
		name=matcher.group(2)
		names[nid]=name

	matcher=re.match(">", inline)
	if matcher != None:
		chunk_id+=1
	matcher=re.match("<", inline)
	if matcher != None:
		chunk_id-=1

	target=print_screen()
	if target != None:
		k=predict(target)
		if k in names:
			lastCommand="%s %s # (%s)" % (target, k, names[k])

	# print (names)
	# print (entities)
	print (lastCommand)

