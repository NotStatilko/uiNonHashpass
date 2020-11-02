import random

from hashlib import (
    sha3_256, blake2b, sha3_512, shake_256, 
    sha1, shake_128, sha384, sha512, sha224, 
    blake2s, sha3_224, sha256, md5, sha3_384
)
from itertools import cycle

hashfuncs = [
    sha3_256, blake2b, sha3_512, shake_256, 
    sha1, shake_128, sha384, sha512, sha224, 
    blake2s, sha3_224, sha256, md5, sha3_384
]
def hashpass(phrase: str, unique_word: str, iterations: int, queue=None) -> shake_256:
    '''
    Args:
        phrase (str): Bitcoin's BIP39 phrase or your password. Will be used as a 
           master-key for all your passwords.

        unique_word (str): Unique word to restore your password. It can be a name
            of service or anything like this. E.g "gmail: mail@gmail.com".

        iterations (int): Number of iterations over hash functions. You can set this as
            a constant number or change it for every service. Anyway i STRONGLY
            suggest you choose a big number (starting from 10,000,000) to
            fully protect you from bruteforcing. The larger this value, the longer 
            it will take to generate the password and the stronger the protection.  
            Don't choose too obvious for attacker numbers.

    Returns:
        The shake_256 object. You can get hash of x bytes with "returned.digest(x)"

    Raises:
        TypeError: If you pass to function bytes instead of str.
    '''
    initkey = sha3_512(''.join((phrase, unique_word, str(iterations))).encode()).digest()
    # initkey is seed of PRNG which shuffle list of hashfuncs

    random_seed = random; random_seed.seed(initkey)
    hashfuncs_copy = hashfuncs[:]; random_seed.shuffle(hashfuncs_copy)
    cycled_hashfuncs_copy = cycle(hashfuncs_copy) # cycled shuffled hashfuncs

    for _ in range(iterations):
        hashfunc = next(cycled_hashfuncs_copy)
        initkey = hashfunc(initkey)
        try:
            initkey = initkey.digest()
        except TypeError: #shake requires digest size
            initkey = initkey.digest(64)
   
    if queue:
        queue.put(shake_256(initkey).hexdigest(32))
