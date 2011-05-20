import cProfile
import pstats

if __name__ == '__main__':
    cProfile.run('import main; main.main()', 'profile_stats')
    stats = pstats.Stats('profile_stats')
    stats.sort_stats('time')
    stats.print_stats('/home/talisein/waether',.2)