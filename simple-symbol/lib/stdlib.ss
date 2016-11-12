" num2str()
" in Tape 1: num  index  positive?  *data
[-]++++{                    " Initialize reference
    < (+@)~(!+)+`           " Copy value to tape 1 index 0
    ?<<_-(!+@*)?!>>+<<?$    " If negative call abs(), else set positive flag
    >+++<                   " Set up jump index
    ?>>[
        #@(!+)              " Jump to data buffer
        +@_%(!++**++)       " Add the num and modulo by 10
        +(!+++****)         " Add 48
        #_/(!++**++)        " Return to 0 index and divide num by 10
        >+<                 " Increment index
    ]
    #(!+)                   " Go to buffer
    [.<]                    " Output
}
