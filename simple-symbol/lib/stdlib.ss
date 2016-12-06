" num2str()
" Memory: num  index  positive?  *data
[-]++++{                " Initialize reference
    < (+@)~(!+)#+`      " Copy value to tape 1 index 0
    ?<<-(!+@*)?!>>+<<?$ " If negative call abs(), else set positive flag
    >+++<               " Set up jump index
    ?>>[
        #@(!+)          " Jump to data buffer
        +@_%(!++**++)   " Add the num and modulo by 10
        +(!+++****)     " Add 48
        #_/(!++**++)    " Return to 0 index and divide num by 10
        >+<             " Increment index
    ]
    -                   " Decrement index
    #(!++)              " Jump to positive flag
    ?<<.(!+++^*(!+++++))?$" If negative, output "-"
    #(!+)               " Go to index
    ?>=(!+++)[          " while index >= 3:
        .(!+@@)         " Output where the index points
        -               " Decrement index
    ]
}[-]

" str2num()
" Memory: index  sign/positive flag  *data
"[-]+++++{
"    (+~**+#)~(!+)#+`    " Copy reference
"    >+@@                " Read the first char
"    ?++(!+++^*(!+++++))
