import argparse
import random

# simulate a single extraction
def pick(count: int=5):
    extracted = []
    while len(extracted) < count:
        r = random.randint(1, 90)
        if (r not in extracted):
            extracted.append(r)
    return extracted

def serialize(extraction: list):
    return " ".join([str(r) for r in extraction])

# keep rolling until a match with the server roll
def potential_seeds(guess: int, days: int=10):
    s = 0
    while s < days * 86400:
        yield guess + s
        yield guess - s
        s += 1 

def bruteforce(target: str, guesses: list):
    for seed in guesses:
        random.seed(seed)
        if serialize(pick(5)) == target:
            return seed
    return -1

# retrieve the seed from the cli
def main():
    parser = argparse.ArgumentParser(
        description='Guess the server seed.')
    parser.add_argument(
        'guess',
        metavar='guess',
        type=int,
        help='the guessed seed, ie the timestamp of the request')
    parser.add_argument(
        'target',
        metavar='target',
        type=str,
        help='the extraction generated by the server')
    parser.add_argument(
        'delta',
        metavar='delta',
        type=int,
        help='the maximum delta to the original guess')

    args = parser.parse_args()

    seed = bruteforce(
        target=args.target,
        guesses=potential_seeds(
            guess=args.guess,
            days=args.delta))

    if seed == -1:
        print("[-] The server seed is outside of our guesses!..")
    else:
        print("[!] Seed found: {}".format(seed))

if __name__ == '__main__':
    main()
