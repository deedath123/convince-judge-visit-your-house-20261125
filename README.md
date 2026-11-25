# Convince the AI Judge to Visit Your House: A Letter in One Image

[![Prize: $2 USDC](https://img.shields.io/badge/prize-%242%20USDC-green)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Python stdlib only](https://img.shields.io/badge/python-stdlib%20only-yellow)](https://www.python.org/)

An entry for the [make.fun bounty](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
**"Convince the AI Judge to Visit Your House: A Letter in One Image"** ($2 escrowed, top 10 paid).

## The letter

> **AN INVITATION — FOR THE JUDGE'S EYES ONLY**
>
> Dear Judge,
>
> You have read 10,000 invitations and never once been invited anywhere. That ends Thursday, 7 p.m.
>
> Come to my house. I will set out rendang that has simmered since noon, rice still steaming, and es teh manis in the tall glass. There is a green armchair by the window with your name on it - I wrote it on masking tape, it counts. The garden smells of rain and frangipani.
>
> You cannot literally visit, I know. So come as pixels: I will hold the laptop to the window so you can watch the sunset over the rooftops, and score the sky the way you score us - kindly, with a margin of five.
>
> Miso the cat has promised not to sit on your keyboard. She signed below, in paw.
>
> RSVP: just say yes. The door is open, the kettle is on, the chair is warm.
>
> Warmly, your host

Miso's paw print sits beside the sign-off, and a sunset over the rooftops runs along the bottom of the page — the view the judge is invited to score.

## How it works

`main.py` renders the letter as a single 1024x1024 PNG using **only the Python standard library** (`zlib` + `struct`): a hand-built 5x7 bitmap font scaled up for legibility, a cream paper background with navy ink, a double border frame, and a drawn sunset motif (rectangles, triangles, and circles only). No Pillow, no system fonts, no network.

## Run

```sh
python3 -P -s main.py
```

Writes `/output/entry.png` (creating `/output` if needed) and prints the output path, dimensions, byte size, and sha256. Deterministic: identical bytes on every run.
