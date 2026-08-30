// Zensical 版で Mermaid の図を描く。
//
// Zensical は ```mermaid を <pre class="mermaid"> にするだけで、描画は行わない。
// 描画用のファイルも同梱しない。そのため、ここで自分で描く。
//
// 読み込む mermaid.min.js は tools/vendor/ の写しである。CDN からは読まない。
// 生成したサイトが外部へ通信しないようにするためである。
//
// 明暗の切り替えに追従する。Zensical は body の data-md-color-scheme を
// "default"（明るい）と "slate"（暗い）で切り替える。図は一度描くと SVG に
// 置き換わるため、元の記法を控えておき、切り替えのたびに描き直す。

(function () {
  if (typeof mermaid === "undefined") { return; }

  var sources = [];

  function isDark() {
    return document.body.getAttribute("data-md-color-scheme") === "slate";
  }

  function render() {
    var nodes = document.querySelectorAll("pre.mermaid");
    if (!nodes.length) { return; }

    // 最初の1回だけ、元の記法を控える。
    if (!sources.length) {
      nodes.forEach(function (node) { sources.push(node.textContent); });
    }

    nodes.forEach(function (node, i) {
      node.removeAttribute("data-processed");
      node.textContent = sources[i];
    });

    mermaid.initialize({
      startOnLoad: false,
      theme: isDark() ? "dark" : "default",
      securityLevel: "strict",
      fontFamily: '"Hiragino Sans", "Noto Sans JP", system-ui, sans-serif'
    });

    try {
      mermaid.run({ querySelector: "pre.mermaid" });
    } catch (e) {
      // 1つの図が壊れていても、ページ全体は読めるようにする。
    }
  }

  render();

  // 明暗の切り替えを見張る。属性が変わったときだけ描き直す。
  var scheme = document.body.getAttribute("data-md-color-scheme");
  new MutationObserver(function () {
    var now = document.body.getAttribute("data-md-color-scheme");
    if (now !== scheme) {
      scheme = now;
      render();
    }
  }).observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });
})();
