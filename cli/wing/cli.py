import argparse

from .core import generate_cli as core_generate_cli
from .CharactersFacet import generate_cli as characters_generate_cli
from .Diamond import generate_cli as diamond_generate_cli
from .DiamondCutFacet import generate_cli as diamond_cut_generate_cli
from .DiamondLoupeFacet import generate_cli as diamond_loupe_generate_cli
from .OwnershipFacet import generate_cli as ownership_generate_cli
from .MockTerminus import generate_cli as terminus_generate_cli
from .version import VERSION


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Wing: Command line interface to Great Wyrm contracts"
    )
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.set_defaults(func=lambda _: parser.print_help())

    subparsers = parser.add_subparsers()

    core_parser = core_generate_cli()
    subparsers.add_parser("core", parents=[core_parser], add_help=False)

    characters_parser = characters_generate_cli()
    subparsers.add_parser("characters", parents=[characters_parser], add_help=False)

    diamond_parser = diamond_generate_cli()
    subparsers.add_parser("diamond", parents=[diamond_parser], add_help=False)

    diamond_cut_parser = diamond_cut_generate_cli()
    subparsers.add_parser("diamond-cut", parents=[diamond_cut_parser], add_help=False)

    diamond_loupe_parser = diamond_loupe_generate_cli()
    subparsers.add_parser(
        "diamond-loupe", parents=[diamond_loupe_parser], add_help=False
    )

    ownership_parser = ownership_generate_cli()
    subparsers.add_parser("ownership", parents=[ownership_parser], add_help=False)

    terminus_parser = terminus_generate_cli()
    subparsers.add_parser("terminus", parents=[terminus_parser], add_help=False)

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
