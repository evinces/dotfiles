return {
  {
    "catppuccin/nvim",
    name = "catppuccin",
    lazy = false,
    priority = 1000,
    config = function()
      local generated_module = "generated_colors"
      local color_path = vim.fn.stdpath("config") .. "/lua/" .. generated_module .. ".lua"

      local function load_theme()
        package.loaded[generated_module] = nil

        local ok, colors = pcall(require, generated_module)
        if not ok then
          return
        end

        require("catppuccin").setup({
          transparent_background = true,
          flavour = "mocha",
          color_overrides = {
            mocha = colors,
          },
          integrations = {
            cmp = true,
            gitsigns = true,
            nvimtree = true,
            treesitter = true,
            notify = true,
            mini = {
              enabled = true,
              indentscope_color = "",
            },
          },
        })

        vim.cmd.colorscheme("catppuccin")
      end

      load_theme()

      local w = vim.uv.new_fs_event()
      w:start(
        color_path,
        {},
        vim.schedule_wrap(function()
          print("Wallust colors updated!")
          load_theme()
        end)
      )
    end,
  },
}
