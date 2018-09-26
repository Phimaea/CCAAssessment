import spacy
import requests
import bs4
import os

nlp = spacy.load('en_core_web_sm')
question = "doLoop"

print("Please Enter A Question:")
question = nlp(input())
    
while str(question) != "end":
    ### Parsing the question ###
    

    questionDictionary = ["HOW", "WHEN", "WHAT", "WHY", "WHERE", "WHO"]
    questionType = ""
    pageName = ""
    extraInfo = []
    if "HOW MANY" in str(question).upper():
        questionType = "HOW MANY"

    for word in question:
        if word.text.upper() in questionDictionary and questionType == "":
            questionType = word.text.upper()
        elif word.pos_ == "PROPN":
            if pageName == "":
                pageName = word.text
            else:
                pageName += "_" + word.text
        elif word.pos_ == "NUM" or word.pos_ == "NOUN":
            extraInfo.append(word.text)
        elif word.pos_ == "VERB" and word.lemma_ != "be":
            extraInfo.append(word.text)
    

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

    ### Store only the content in the <p> brackets ###
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


    ### Start searching through the gathered information. ###

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

    #<testing>
    #print()
    #print("-#-")
    #for sentance in relevantSentances:
    #    print(" - ")
    #    print(sentance)
    #</testing>

    answer = ""

    ### WHEN ###
    if questionType == "WHEN":
        for sentance in relevantSentances:
            sentance = nlp(sentance)
            months = ["january","february","march","april","may","june","july","august","september","october","november","december"]
            for word in sentance:
                if word.shape_ == "dddd" and answer == "" or answer == "" and word.shape_ == "ddxx": #year
                    answer = str(sentance)
                    break

    ### WHAT ###
    elif questionType == "WHAT":
        if len(extraInfo) == 0: #if there is no extra info to go off, guess at the first line of wikipedia.
            for letter in content:
                answer += letter
                if letter == ".":
                    break
        else:
            answer = str(relevantSentances)

    ### WHY ###
    elif questionType == "WHY":
        for sentance in relevantSentances:
            for word in sentance.split(" "):
                if word.lower() == "because" and answer == "":
                    answer = str(sentance)
        
    ### WHERE ###
    elif questionType == "WHERE":
        for sentance in relevantSentances:
            sentance = nlp(sentance)
            for word in sentance.ents:
                if word.label_ == "GPE" and answer == "":
                    answer = str(sentance)
        
    ### WHO ###
    elif questionType == "WHO":
        for sentance in relevantSentances:
            sentance = nlp(sentance)
            if answer == "":
                for word in sentance.ents:
                    if word.label_ == "PERSON" and answer == "":
                        answer = str(sentance)

        if len(extraInfo) == 0: #if there is no extra info to go off, guess at the first line of wikipedia.
            for letter in content:
                answer += letter
                if letter == ".":
                    break
                    
    ### HOW ###
    elif questionType == "HOW":
        for sentance in relevantSentances:
            answer = str(sentance)

    ### HOW MANY ###
    elif questionType == "HOW MANY":
        for sentance in relevantSentances:
                sentance = nlp(sentance)        
                for word in sentance:
                    if word.pos_ == "NUM":
                        answer = str(sentance)
                        break

    ### Print answer if you have it
    if answer == "":
        print("Sorry, I don't know the answer.")
    else:
        print("ANSWER: " + answer)


    # testing #
    #print("PAGENAME: " + pageName)
    #print("QUESTION TYPE: " + questionType)
    #print("EXTRA INFO: " + str(extraInfo))
    #print("RELEVANT SENTANCES: " + str(relevantSentances))
    #print("-----------------------------------------------------")
    #print(content)
    #print("-----------------------------------------------------")
    # end testing #

    #Allow the user to enter another question
    print()
    print("(Enter 'end' to end the program.)")
    print("Please Enter A Question:")
    question = nlp(input())
