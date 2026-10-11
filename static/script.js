(() => {
  const $ = (selector) => document.querySelector(selector);
  const display = $("#display");
  const expression = $("#expression");
  const error = $("#error");
  const historyPanel = $("#history-panel");
  const historyList = $("#history-list");
  const menu = $("#menu");
  const scrim = $("#scrim");
  const advancedToggle = $("#advanced-toggle");
  const advancedFunctions = $("#advanced-functions");

  let current = "0";
  let stored = null;
  let operator = null;
  let resetOnDigit = false;

  const symbols = { "+": "+", "−": "−", "×": "×", "÷": "÷", mod: "mod", power: "^", percentage: "% of" };
  const operationNames = { "+": "add", "−": "subtract", "×": "multiply", "÷": "divide", mod: "modulus", power: "power", percentage: "percentage" };

  const clean = (n) => {
    const value = Number(n);
    if (!Number.isFinite(value)) throw new Error("Result is undefined or too large.");
    return String(Number(value.toPrecision(12)));
  };
  const showError = (message = "") => { if (error) error.textContent = message; };
  function render() {
    display.textContent = current;
    expression.textContent = stored !== null && operator ? `${stored} ${symbols[operator] || operator}` : (expression.dataset.value || "");
  }
  function clearAll() {
    current = "0"; stored = null; operator = null; resetOnDigit = false;
    expression.dataset.value = "";
    showError(""); render();
  }
  function enterDigit(digit) {
    showError("");
    if (current === "Error" || resetOnDigit) { current = digit; resetOnDigit = false; }
    else if (current === "0") current = digit;
    else if (current.replace("-", "").replace(".", "").length < 15) current += digit;
    render();
  }
  function enterDecimal() {
    showError("");
    if (current === "Error" || resetOnDigit) { current = "0"; resetOnDigit = false; }
    if (!current.includes(".")) current += ".";
    render();
  }
  async function apiCalculate(type, a, b) {
    const payload = { operation: type, a };
    if (b !== undefined) payload.b = b;
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok || data.success === false || data.error) throw new Error(data.error || "Calculation failed.");
    return data;
  }
  async function loadHistory() {
    try {
      const response = await fetch("/api/history");
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to load history.");
      renderHistory(Array.isArray(data.history) ? data.history : []);
    } catch (e) { showError(e.message); }
  }
  function renderHistory(items = []) {
    historyList.replaceChildren();
    if (!items.length) {
      const empty = document.createElement("p");
      empty.className = "empty-history"; empty.textContent = "No calculations yet.";
      historyList.append(empty); return;
    }
    items.slice().reverse().forEach((entry) => {
      const item = document.createElement("article"); item.className = "history-item";
      item.textContent = typeof entry === "string" ? entry : `${entry.label} = ${entry.answer}`;
      historyList.append(item);
    });
  }
  async function clearHistory() {
    try {
      const response = await fetch("/api/history", { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not clear history.");
      renderHistory([]); showError("");
    } catch (e) { showError(e.message); }
  }
  async function runEquals() {
    if (stored === null || !operator || resetOnDigit || current === "Error") return;
    const a = Number(stored), b = Number(current), op = operator;
    showError("");
    try {
      const data = await apiCalculate(operationNames[op], a, b);
      current = data.display_result ?? clean(data.result);
      expression.dataset.value = data.calculation || `${stored} ${symbols[op] || op} ${current}`;
      stored = null; operator = null; resetOnDigit = true;
      showError(""); render(); await loadHistory();
    } catch (e) { showError(e.message); }
  }
  function chooseOperator(next) {
    showError("");
    if (current === "Error") return;
    if (stored !== null && operator && !resetOnDigit) {
      // Finish the pending operation first; users can continue with the result.
      runEquals().then(() => {
        stored = current; operator = next; resetOnDigit = true; render();
      });
      return;
    }
    stored = current; operator = next; resetOnDigit = true; render();
  }
  async function unary(type) {
    if (current === "Error") return;
    const a = Number(current);
    showError("");
    try {
      const data = await apiCalculate(type, a);
      current = data.display_result ?? clean(data.result);
      expression.dataset.value = data.calculation || `${type}(${a})`;
      resetOnDigit = true; stored = null; operator = null;
      render(); await loadHistory();
    } catch (e) { showError(e.message); }
  }
  function percent() {
    if (current === "Error") return;
    try { current = clean(Number(current) / 100); resetOnDigit = true; showError(""); render(); }
    catch (e) { showError(e.message); }
  }
  function backspace() {
    if (current === "Error" || resetOnDigit) { current = "0"; resetOnDigit = false; }
    else current = current.length > 1 ? current.slice(0, -1) : "0";
    if (current === "-") current = "0";
    showError(""); render();
  }
  function toggleSign() {
    if (current !== "Error" && Number(current) !== 0) current = current.startsWith("-") ? current.slice(1) : `-${current}`;
    render();
  }
  function openHistory() {
    historyPanel.classList.add("open"); historyPanel.setAttribute("aria-hidden", "false");
    scrim.hidden = false; closeMenu(); loadHistory();
  }
  function closeHistory() {
    historyPanel.classList.remove("open"); historyPanel.setAttribute("aria-hidden", "true");
    scrim.hidden = true;
  }
  function closeMenu() {
    menu.hidden = true; $("#menu-toggle").setAttribute("aria-expanded", "false");
  }
  function toggleTheme() {
    const root = document.documentElement;
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem("calculator-theme", root.dataset.theme); } catch (_) {}
  }

  document.querySelector(".keypad").addEventListener("click", (event) => {
    const button = event.target.closest("button"); if (!button) return;
    if (button.dataset.digit !== undefined) enterDigit(button.dataset.digit);
    else if (button.dataset.operator) chooseOperator(button.dataset.operator);
    else switch (button.dataset.action) {
      case "clear": clearAll(); break;
      case "sign": toggleSign(); break;
      case "percent": percent(); break;
      case "backspace": backspace(); break;
      case "decimal": enterDecimal(); break;
      case "equals": runEquals(); break;
    }
  });
  document.querySelector(".extras").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-extra]"); if (!button) return;
    const type = button.dataset.extra;
    if (["square", "cube", "square_root", "cube_root"].includes(type)) { await unary(type); return; }
    if (["power", "modulus"].includes(type)) { chooseOperator(type === "power" ? "power" : "mod"); return; }
    if (type === "percentage") {
      const first = Number(current);
      const second = prompt("Enter the number to calculate this percentage of:");
      if (second === null || second.trim() === "" || !Number.isFinite(Number(second))) return;
      try {
        const data = await apiCalculate("percentage", first, Number(second));
        current = data.display_result ?? clean(data.result);
        expression.dataset.value = data.calculation || `${first}% of ${Number(second)}`;
        resetOnDigit = true; render(); await loadHistory();
      } catch (e) { showError(e.message); }
    }
  });

  advancedToggle.addEventListener("click", () => {
    const isExpanded = advancedToggle.getAttribute("aria-expanded") === "true";
    advancedToggle.setAttribute("aria-expanded", String(!isExpanded));
    advancedFunctions.hidden = isExpanded;
    advancedToggle.querySelector(".advanced-label").textContent = isExpanded ? "More functions" : "Hide functions";
  });

  $("#history-toggle").addEventListener("click", openHistory);
  $("#history-close").addEventListener("click", closeHistory);
  scrim.addEventListener("click", closeHistory);
  $("#menu-toggle").addEventListener("click", () => {
    menu.hidden = !menu.hidden;
    $("#menu-toggle").setAttribute("aria-expanded", String(!menu.hidden));
  });
  $("#menu-history").addEventListener("click", openHistory);
  $("#menu-theme").addEventListener("click", () => { toggleTheme(); closeMenu(); });
  $("#theme-toggle").addEventListener("click", toggleTheme);
  $("#menu-clear").addEventListener("click", () => { clearAll(); closeMenu(); });
  $("#clear-history").addEventListener("click", clearHistory);
  document.addEventListener("click", (event) => {
    if (!menu.hidden && !menu.contains(event.target) && !$("#menu-toggle").contains(event.target)) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { closeHistory(); closeMenu(); return; }
    if (/^[0-9]$/.test(event.key)) enterDigit(event.key);
    else if (event.key === ".") enterDecimal();
    else if (event.key === "+") chooseOperator("+");
    else if (event.key === "-") chooseOperator("−");
    else if (event.key === "*") chooseOperator("×");
    else if (event.key === "/") { event.preventDefault(); chooseOperator("÷"); }
    else if (event.key === "Enter" || event.key === "=") runEquals();
    else if (event.key === "Backspace") backspace();
    else if (event.key === "%") percent();
  });

  try {
    const savedTheme = localStorage.getItem("calculator-theme");
    if (savedTheme === "dark" || savedTheme === "light") document.documentElement.dataset.theme = savedTheme;
  } catch (_) {}
  render(); loadHistory();
  console.log("Calculator initialized.");
})();
