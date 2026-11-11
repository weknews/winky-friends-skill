#!/bin/bash
# 로고 시안 생성: gen_logo.sh 이름 크기 "IMAGE 문장" [기준 그림...] → gen/이름.png
# series-kit/gen.sh와 같은 Codex image_gen(Images 2.6) 호출. 인물 줄 세우기·색 잠금·「글자 금지」 문단은 넣지 않는다(로고라 글자를 그리는 시안이 있다).
L="$(cd "$(dirname "$0")" && pwd)"; R="$L/../../style/refs"
name=$1; size=$2; prompt=$3; shift 3
args=(-i "$R/s8-winky.png"); for r in "$@"; do args+=(-i "$r"); done
STYLE="STYLE Paper-Layer: layered cut-paper illustration photographed straight on: crisp shapes cut from matte colored paper, stacked in 3-5 layers with thin soft shadows between layers, visible clean paper edges, faint paper fiber. Simple bold silhouettes. Exactly the same paper style and cute proportions as the attached Winky reference. No glossy shine, no gradients, no sparkles, no hearts, no red, no purple, no medical cross. COLORS: Winky cream #F3E3C8, ear pink #F2A7B5, tail tip dark brown #4A3027 (small areas only), deep navy #10233F, white paper, pale sand. Large areas of red, purple or brown are forbidden. TRANSPARENT BACKGROUND: turn on the image tool's transparent background option and keep the alpha; nothing outside the logo shape. Must be an original series logo, not resembling any existing franchise logo."
timeout 900 codex exec --skip-git-repo-check -s workspace-write -C "$L" "${args[@]}" -- "내장 image_gen 도구로 quality high, 크기 $size, 투명 배경(transparent background) 그림을 한 장 만들어 $L/gen/$name.png 에 저장하라. 코드로 그리지 말고 반드시 image_gen 도구를 써라. 첨부한 그림은 기준 그림이다(그림체, 윙키 생김새). 저장 뒤 파일 경로만 한 줄로 답하라. 프롬프트는 아래를 그대로 쓴다. $STYLE IMAGE: $prompt" < /dev/null > "$L/gen/$name.log" 2>&1
[ -f "$L/gen/$name.png" ] && echo "OK $name" || { echo "FAIL $name"; tail -3 "$L/gen/$name.log"; }
