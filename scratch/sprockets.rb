#!/usr/bin/env ruby
require 'benchmark'

def string_end_with_semicolon_orig?(str)
  i = str.size - 1
  while i >= 0
    c = str[i]
    i -= 1
    if c == "\n" || c == " " || c == "\t"
      next
    elsif c != ";"
      return false
    else
      return true
    end
  end
  true
end

def string_end_with_semicolon_new?(str)
  i = str.size - 1
  while i >= 0
    c = str[i].ord
    i -= 1

    # Need to compare against the ordinals because the string can be UTF_8 or UTF_32LE encoded
    # 0x0A == "\n"
    # 0x20 == " "
    # 0x09 == "\t"
    # 0x3B == ";"
    unless c == 0x0A || c == 0x20 || c == 0x09
      return c === 0x3B
    end
  end

  true
end

def string_end_with_semicolon_regex?(str)
  !!(str =~ /\A[ \n\t]*\z/ || str =~ /;[ \n\t]*\z/)
end

def string_end_with_semicolon_byte?(str)
  i = str.bytesize - 1
  while i >= 0
    c = str.getbyte(i)
    i -= 1

    # 0x0A == "\n"
    # 0x20 == " "
    # 0x09 == "\t"
    # 0x3B == ";"
    unless c == 0x0A || c == 0x20 || c == 0x09
      return c === 0x3B
    end
  end

  true
end

LONGKB = 100
N = 1000

def main
  tests = [
    {name: "ascii-short-no", value: "x"*1024},
    {name: "ascii-short-yes", value: "x"*1024 + ";"},
    {name: "ascii-long-no", value: "x"*1024*LONGKB},
    {name: "ascii-long-yes", value: "x"*1024*LONGKB + ";"},
    {name: "ascii-long-yes-ws", value: "x"*1024*LONGKB + ";" + " "*1024},
    {name: "empty", value: ""},
    {name: "utf8-long-no", value: "\u2665" + "x"*1024*LONGKB},
    {name: "utf8-long-yes", value: "\u2665" + "x"*1024*LONGKB + ";"},
    {name: "utf8-long-yes-ws", value: "\u2665" + "x"*1024*LONGKB + ";" + " "*1024},
  ]
  methods = [
    {name: "old", method: ->x{string_end_with_semicolon_orig?(x)}},
    {name: "new", method: ->x do
       x = x.encode(Encoding::UTF_32LE) unless x.ascii_only?
       string_end_with_semicolon_new?(x)
     end},
    {name: "regex", method: ->x{string_end_with_semicolon_regex?(x)}},
    {name: "byte", method: ->x{string_end_with_semicolon_byte?(x)}},
  ]

  tests.each do |t|
    answers = methods.map { |m| m[:method].call(t[:value]) }
    if answers.uniq.length != 1
      $stderr.puts("methods disagree on #{t[:name]}!")
      methods.each do |m|
        $stderr.puts("  #{m[:name]}: #{m[:method].call(t[:value])}")
      end
    end
  end

  Benchmark.benchmark(Benchmark::CAPTION, 25) do |bm|
    methods.each do |m|
      puts "# #{m[:name]}"
      tests.each do |t|
        bm.report("#{m[:name]}+#{t[:name]}") do
          for _ in 1..N
            m[:method].call(t[:value])
          end
        end
      end
      puts
    end
  end
end

if __FILE__ == $0
  main
end
