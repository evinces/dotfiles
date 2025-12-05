-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Indent in Visual Mode and keep selection
vim.keymap.set("v", "<Tab>", ">gv", { desc = "Indent selection" })

-- De-indent in Visual Mode and keep selection
vim.keymap.set("v", "<S-Tab>", "<gv", { desc = "De-indent selection" })
