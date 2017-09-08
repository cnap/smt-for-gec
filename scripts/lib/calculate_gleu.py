"""calls the GLEU script"""
from gleu import GLEU
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', required=True,
                        help='path to src sentences')
    parser.add_argument('-r', '--ref', nargs='*', required=True,
                        help='references to use')
    parser.add_argument('-d', '--debug', default=False, action='store_true',
                        help='print debugging messages')
    parser.add_argument('-c', '--cand', nargs='*', required=True,
                        help='candidate(s) to score')
    args = parser.parse_args()

    gleu_calculator = GLEU(4)
    gleu_calculator.load_sources(args.src)
    num_iterations = 200
    gleu_calculator.load_references(args.ref)
    for cand in args.cand:
        print cand, [float(g[0]) for g in gleu_calculator.run_iterations(
            num_iterations=num_iterations,
            source=args.src,
            hypothesis=cand,
            per_sent=False)][0]
