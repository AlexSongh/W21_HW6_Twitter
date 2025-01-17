#########################################
##### Name:   Hang Song             #####
##### Uniqname:   02755159          #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import emoji
import operator

import hw6_secrets_starter as secrets # file that contains your OAuth credentials

CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key


def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    response = requests.get(baseurl, params=params, auth=oauth)
    return response.json()


def make_request_with_cache(baseurl, hashtag, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    CACHE_DICT = open_cache()
    params = {'q':hashtag,'count':count}
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("fetching cached data")
        return CACHE_DICT[request_key]
    else:
        print("making new request")
        CACHE_DICT[request_key] = make_request(baseurl, params)
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]


def find_most_common_cooccurring_hashtag(tweet_data, hashtag_to_ignore):
    ''' Finds the hashtag that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache() 
        (e.g. "#MarchMadness2021")

    Returns
    -------
    string
        the hashtag that most commonly co-occurs with the hashtag 
        queried in make_request_with_cache()

    '''
    hashtag_dict = {}
    most_common_cooccurring_hashtag = None
    hashtag_to_ignore = hashtag_to_ignore.replace("#",'')
    hashtag_to_ignore = hashtag_to_ignore.lower()

    for result in tweet_data['statuses']:
        hashtag_list = result['entities']['hashtags']
        if len(hashtag_list) > 0:
            for i in hashtag_list:
                ht = i['text'].lower()
                if ht!= hashtag_to_ignore:
                    if ht not in hashtag_dict:
                        hashtag_dict[ht] = 1
                    else:
                        hashtag_dict[ht] = hashtag_dict[ht]+1

    
    most_common_cooccurring_hashtag = max(hashtag_dict,key = hashtag_dict.get)

    return most_common_cooccurring_hashtag
    # return (hashtag_dict)

    ''' Hint: In case you're confused about the hashtag_to_ignore 
    parameter, we want to ignore the hashtag we queried because it would 
    definitely be the most occurring hashtag, and we're trying to find 
    the most commonly co-occurring hashtag with the one we queried (so 
    we're essentially looking for the second most commonly occurring 
    hashtags).'''


def find_most_common_3_cooccurring_hashtag(tweet_data, hashtag_to_ignore):
    ''' Finds the hashtag that top 3 most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache() 
        (e.g. "#MarchMadness2021")

    Returns
    -------
    tuple or None
        the top 3 hashtag that most commonly co-occurs with the hashtag 
        queried in make_request_with_cache()

    '''
    hashtag_dict = {}
    found_dict = {}
    hashtag_to_ignore = hashtag_to_ignore.replace("#",'')
    hashtag_to_ignore = hashtag_to_ignore.lower()

    for result in tweet_data['statuses']:
        hashtag_list = result['entities']['hashtags']
        if len(hashtag_list) > 0:
            for i in hashtag_list:
                ht = i['text'].lower()
                if ht!= hashtag_to_ignore:
                    if ht not in hashtag_dict:
                        hashtag_dict[ht] = 1
                    else:
                        hashtag_dict[ht] = hashtag_dict[ht]+1

    if len(hashtag_dict.keys()) >= 3:
        firstnum = max(hashtag_dict.values())
        first_key = max(hashtag_dict,key = hashtag_dict.get)
        found_dict[first_key] = firstnum
        del hashtag_dict[first_key]

        #Find the 2nd con-occuring hashtag
        secondnum = 0
        second_key = None
        for num in hashtag_dict.values():
            if num > secondnum and num <= firstnum:
                secondnum = num
        for key,value in hashtag_dict.items():
            if value == secondnum:
                second_key = key
        found_dict[second_key] = secondnum
        del hashtag_dict[second_key]

        #Find the 3rd con-occuring hashtag
        thirdnum = 0
        third_key = None
        for num in hashtag_dict.values():
            if num > thirdnum and num <= secondnum:
                thirdnum = num
        for key,value in hashtag_dict.items():
            if value == thirdnum:
                third_key = key
        found_dict[third_key] = thirdnum
        del hashtag_dict[third_key]

        return (first_key, second_key, third_key)

    elif len(hashtag_dict.keys()) == 2:
        firstnum = max(hashtag_dict.values())
        first_key = max(hashtag_dict,key = hashtag_dict.get)
        found_dict[first_key] = firstnum
        del hashtag_dict[key]
        #Find the 2nd con-occuring hashtag
        secondnum = 0
        second_key = None
        for num in hashtag_dict.values():
            if num > secondnum and num <= firstnum:
                secondnum = num
        for key,value in hashtag_dict.items():
            if value == secondnum:
                second_key = key
        found_dict[second_key] = firstnum
        del hashtag_dict[second_key]
        return (first_key, second_key)

    elif len(hashtag_dict.keys()) == 1:
        firstnum = max(hashtag_dict.values())
        first_key = max(hashtag_dict,key = hashtag_dict.get)
        return (first_key)
    elif len(hashtag_dict.keys()) == 0:
        return None

def find_ten_most_common_words(tweet_data, hashtag, word_list):
    ''' Finds 10 words that are most common in the text associated with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag: string
        the same hashtag that is queried in make_request_with_cache() 
        (e.g. "#MarchMadness2021")
    wordlist: list
        a list of the stop words that you should ignore when counting the text.

    Returns
    -------
    strings
        10 words that are most common associated with the hashtag 
        queried in make_request_with_cache()

    '''

    text_list = []
    hashtag = hashtag.replace("#",'')
    hashtag = hashtag.lower()
    accumulator = {}

    for result in tweet_data['statuses']:
        text_list.append(result['text'])

    for text in text_list:
        text = text.lower()
        text_clean = emoji.get_emoji_regexp().sub("", text)
        list_clean = text_clean.split()
        for word in list_clean:
            if not word.startswith("@"):
                if not word.startswith('#'):
                    if word not in word_list:
                        if not word.isnumeric():
                            if 'https:' not in word:
                                if len(word)>1:
                                    word.encode('ascii','ignore')
                                    word = word.replace(',','').replace('.','').replace(';','')
                                    if word not in accumulator.keys():
                                        accumulator[word] = 1
                                    else:
                                        accumulator[word] = accumulator[word]+1

    # sort the values in the dictionary by desending order 
    sorted_l = list( sorted(accumulator.items(), key=operator.itemgetter(1),reverse=True))
    
    # print the top 10 keys (common words)
    print("Extra credit 2: list out the 10 most common words in the tweet text associated with the hashtag that you input:")
    for i in range(10):
        print(sorted_l[i])


if __name__ == "__main__":
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secret_data.py.")
        exit()

    CACHE_DICT = open_cache()

    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    count = 100

    ### Extra Credit 1 ###
    
    while True:
        hashtag = input("EC1: Please enter a hashtag that you wanna search starting with #, enter exit to leave: ")
        if hashtag == "exit":
            break
        else:
            tweet_data = make_request_with_cache(baseurl, hashtag, count)
            hashtag_tuple = find_most_common_3_cooccurring_hashtag(tweet_data,hashtag)

            if hashtag_tuple != None:
                if len(hashtag_tuple)>=3:
                    print("The most top three commonly co-occurring hashtag with {} is #{}, #{} and #{}.".format(hashtag, hashtag_tuple[0], hashtag_tuple[1], hashtag_tuple[2]))
                elif len(hashtag_tuple) == 2:
                    print("The most top two commonly co-occurring hashtag with {} is #{} and #{}.".format(hashtag, hashtag_tuple[0], hashtag_tuple[1]))
                elif len(hashtag_tuple) == 1:
                    print("The most top commonly co-occurring hashtag with {} is #{}.".format(hashtag, hashtag_tuple[0]))
            else:
                print("There is no other co-occuring hashtags that match your search.")
    

    ### Extra Credit 2 ###
    f = open("stop_word.txt","r")
    stop_word_list = f.read().splitlines()
    f.close()
    # print(stop_word_list)

    # Also ignore RT, so append it to the list
    stop_word_list.append("rt")  #lower case
    tweet_data = make_request_with_cache(baseurl, hashtag, count)

    # Interactive program
    while True:
        hashtag = input("EC2: Please enter a hashtag beginning with # to find 10 common words, enter exit to leave: ")
        if hashtag == "exit":
            break
        else:
            tweet_data = make_request_with_cache(baseurl, hashtag, count)
            find_ten_most_common_words(tweet_data,hashtag,stop_word_list)











