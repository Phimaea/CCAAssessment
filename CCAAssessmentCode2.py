import spacy
import requests
import bs4
import os

nlp = spacy.load('en_core_web_sm')

### FUNCTIONS ###

def GetContent(soup):
    ### Gather info from web page - store only the content in the <p> brackets ###
    tagBoolean = False
    tag = ""
    content = ""
    recording = False

    for char in str(soup):
        if char == "<":
            tag = "<"
            tagBoolean = True
        elif char == ">":
            tag += ">"
            tagBoolean = False
            if tag == "<p>":
                recording = True
            elif tag == "</p>":
                recording = False
        elif tagBoolean == True:
            tag += char
        elif recording == True:
            content += char
    #Pass back the content collected
    return content

def FindRelevant():
     ### Search gathered info for relevant sentances. ###

    #declare variables
    relevantSentances = []

    if len(extraInfo) != 0: #there is some info
        #local variables
        tempSentance = ""
        relevant = False
        for word in content.split(" "):
             #store words in a temporary sentance so can judge if it is important
             tempSentance += str(word) + " "
             #check extraInfo to see if sentance is relevant
             for info in extraInfo:
                 if info == word:
                     relevant = True

             #end of sentance
             if "." in str(word):
                 if relevant == True: #store the sentance if relevant
                     relevantSentances.append(tempSentance)
                 #reset variables
                 tempSentance = ""
                 relevant = False
    #Sort the sentances
    relevantSentances = sortByRelevance(relevantSentances)
    #Pass back the relevant sentances
    return relevantSentances
    
def When():
    ans = ""
    for sentance in relevantSentances:
            sentance = nlp(sentance)
            months = ["january","february","march","april","may","june","july","august","september","october","november","december"]
            for word in sentance:
                if word.shape_ == "dddd" and ans == "" or ans == "" and word.shape_ == "ddxx" or ans == "" and str(word).lower() in months: #sentance contains a year or a month
                    ans = str(sentance)
                    break
    return ans                

## Deal with the different types of questions ##
                
def What():
    ans = ""
    if len(extraInfo) == 0: #if there is no extra info to go off, guess at the first line of wikipedia.
       for letter in content:
            ans += letter
            if letter == ".":
                break
            else:
                ans = str(relevantSentances)
    return ans
            
def Why():
    ans = ""
    for sentance in relevantSentances:
            for word in sentance.split(" "):
                if word.lower() == "because" and ans == "":
                    ans = str(sentance)
    return ans
                    
def Where():
    ans = ""
    for sentance in relevantSentances:
            sentance = nlp(sentance)
            for word in sentance.ents:
                if word.label_ == "GPE" and ans == "":
                    ans = str(sentance)
    return ans

def Who():
    ans = ""
    for sentance in relevantSentances:
        sentance = nlp(sentance)
        if ans == "":
            for word in sentance.ents:
                if word.label_ == "PERSON" and ans == "":
                    ans = str(sentance)

        if len(extraInfo) == 0: #if there is no extra info to go off, guess at the first line of wikipedia.
            for letter in content:
                ans += letter
                if letter == ".":
                    break
    return ans

def HowMany():
    for sentance in relevantSentances:
                sentance = nlp(sentance)        
                for word in sentance:
                    if word.pos_ == "NUM":
                        ans = str(sentance)
                        break
    return ans

def sortByRelevance(rSentances):
    if len(rSentances) > 1:
        scores = []
        #Score the sentances
        for sentance in rSentances:
            score = 0
            for info in extraInfo:
                if info in sentance:
                    score += 1
            scores.append(score)
        #Sort the sentance in order of score
        for i in range(0, len(rSentances)-2):
            if (scores[i] > scores[i+1]):
                #if next score is larger than this
                #store current score & corresponding sentance in temp variables
                tempScore = scores[i]
                tempSentance = rSentances[i]
                #Update the scores
                scores[i] = scores[i+1]
                rSentances[i] = rSentances[i+1]
                scores[i+1] = tempScore
                rSentance[i+1] = tempSentance
                #Rerun the loop
                i=0
    return rSentances
            

### PROGRAM LOOP ###
print("Please Enter A Question:")
question = nlp(input())
    
while str(question) != "end":
    #Declare Variables
    questionDictionary = ["HOW", "WHEN", "WHAT", "WHY", "WHERE", "WHO"]
    questionType = ""
    pageName = ""
    extraInfo = []
    
    #Check if question is a 'how many' - more than one question word
    if "HOW MANY" in str(question).upper():
        questionType = "HOW MANY"
    #Parse the question
    for word in question:
        if word.text.upper() in questionDictionary and questionType == "":
            #If this is the question word, store it as questionType
            questionType = word.text.upper()
        elif word.pos_ == "PROPN":
            #Format the page name for Wikipedia
            if pageName == "":
                pageName = word.text
            else:
                pageName += "_" + word.text
        elif word.pos_ == "NUM" or word.pos_ == "NOUN":
            #Store any extra information
            extraInfo.append(word.text)
        elif word.pos_ == "VERB" and word.lemma_ != "be":
            #Store extra info, excluding 'be' as is mostly irrelevant to question
            extraInfo.append(word.text)
    
    #If no proper nouns have been found to be the page name, attempt to create one from the extra info gathered
    if pageName == "":
        extraInfo = str(extraInfo)
        extraInfo = extraInfo.replace("[","")
        extraInfo = extraInfo.replace("]","")
        extraInfo = extraInfo.replace("'","")
        for i in range(0,len(extraInfo)):
            if i == 0:
                pageName += extraInfo[i].upper()
            else:
                pageName += extraInfo[i]
        extraInfo = []

    ### Get info from Wikipedia ###

    #stores the name of the wikipedia page
    pageName = "https://en.wikipedia.org/wiki/" + pageName
    #gets the information from the page
    page = requests.get(pageName)
    #sorts the information into all the html
    soup = bs4.BeautifulSoup(page.text, "html.parser")

    if "Wikipedia does not have an article with this exact name" in str(soup):
        print("There is no Wikipedia page on this subject.")

    ### Gather info from web page - store only the content in the <p> brackets ###
    content = GetContent(str(soup))


    ### Start searching through the gathered information. ###

    #declare variables
    relevantSentances = FindRelevant()


    answer = ""

    if questionType == "WHEN":
        answer = When()
    elif questionType == "WHAT":
        answer = What()
    elif questionType == "WHY":
        answer = Why()
    elif questionType == "WHERE":
        answer = Where()
    elif questionType == "WHO":
        answer = Who()            
    elif questionType == "HOW":
        for sentance in relevantSentances:
            answer = str(sentance)
    elif questionType == "HOW MANY":
        answer = HowMany()
        

    ### Print answer if you have it
    if answer == "":
        print("Sorry, I don't know the answer.")
    else:
        print("ANSWER: " + answer)


    #Allow the user to enter another question
    print()
    print("(Enter 'end' to end the program.)")
    print("Please Enter A Question:")
    question = nlp(input())

#End Program Loop
exit()

